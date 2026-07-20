"""Browser-level test of the Plan trips flow, added per the 2026-07-20
post-alignment audit: the audit caught a form-destruction crash that
API tests and DOM-stub harnesses could not see, so a real browser now
drives the real page. Enters constraints, submits the form, receives
recommendation cards, opens a trip detail, and returns.

The map CDN is stubbed via request interception (this sandbox cannot
reach unpkg.com); everything else is the real served page against a
real HTTP server with an injected availability fetcher.

SKIPS cleanly (exit 0 with a SKIP message) when playwright or a
chromium binary is unavailable, so the suite still runs on machines
without a browser; it must NOT be skipped in CI-capable environments.
"""
import os
import sys
import threading
import time
import urllib.request
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PORT = 8797
D0 = date(2026, 8, 14)

LEAFLET_STUB = """
(function(){
  function chain(){ var o={}; ['setView','addTo','on','off','bindTooltip',
    'fitBounds','remove','addLayer','removeLayer','openOn','setStyle']
    .forEach(function(k){ o[k]=function(){ return o; }; }); return o; }
  var L = {};
  L.map = function(){ var m = chain();
    m.dragging = {enable:function(){},disable:function(){}};
    m.latLngToContainerPoint = function(){ return {x:0,y:0}; };
    return m; };
  ['tileLayer','polyline','circleMarker','marker','layerGroup']
    .forEach(function(k){ L[k]=function(){ return chain(); }; });
  L.divIcon = function(){ return {}; };
  L.latLngBounds = function(){ return {}; };
  window.L = L;
})();
"""


def make_fetch():
    def fetch(pid, divs, start, end):
        out = {}
        for dv in divs:
            out[dv] = {}
            d = start
            while d <= end:
                out[dv][d.isoformat()] = 4
                d += timedelta(days=1)
        return out
    return fetch


def start_server():
    import uvicorn
    from switchback.web import create_app
    config = uvicorn.Config(create_app(fetch_fn=make_fetch()),
                            host="127.0.0.1", port=PORT, log_level="error")
    server = uvicorn.Server(config)
    t = threading.Thread(target=server.run, daemon=True)
    t.start()
    for _ in range(100):
        try:
            urllib.request.urlopen(
                f"http://127.0.0.1:{PORT}/api/plan/defaults", timeout=1)
            return server
        except Exception:
            time.sleep(0.1)
    raise RuntimeError("test server did not come up")


def launch_browser(p):
    try:
        return p.chromium.launch()
    except Exception:
        exe = os.environ.get("PLAYWRIGHT_CHROMIUM",
                             "/opt/pw-browsers/chromium")
        return p.chromium.launch(executable_path=exe)


def main():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("BROWSER SKIP: playwright not installed on this machine")
        return
    server = start_server()
    errors = []
    try:
        with sync_playwright() as p:
            try:
                browser = launch_browser(p)
            except Exception as ex:
                print(f"BROWSER SKIP: no usable chromium ({ex})")
                return
            page = browser.new_page()
            page.on("pageerror", lambda e: errors.append(str(e)))

            def stub(route):
                url = route.request.url
                if url.endswith(".js"):
                    route.fulfill(content_type="application/javascript",
                                  body=LEAFLET_STUB)
                else:
                    route.fulfill(content_type="text/css", body="")
            page.route("**unpkg.com/**", stub)

            page.goto(f"http://127.0.0.1:{PORT}/")
            page.wait_for_selector("#plan")
            page.select_option("#park", "rainier")
            page.wait_for_timeout(400)
            page.fill("#start", D0.isoformat())
            page.fill("#end", D0.isoformat())
            page.fill("#nights", "2")
            page.fill("#party", "2")

            # 1. open the planner, 2. enter constraints
            page.click("#plan")
            page.wait_for_selector("#p_go")
            page.fill("#p_pref_mi", "9")
            page.fill("#p_max_mi", "13")
            page.fill("#p_pref_gain", "2500")
            page.fill("#p_max_gain", "4500")
            page.select_option("#p_pace", "0.85")
            page.check("#p_arrive")
            summary = page.text_content("#p_summary")
            assert "2 backcountry night" in summary, summary

            # 3. submit and receive recommendations
            page.click("#p_go")
            page.wait_for_selector(".card", timeout=20000)
            cards = page.locator(".card").count()
            assert cards > 0, "no recommendation cards rendered"
            assert page.locator("#p_go").is_visible(), \
                "the constraint form must survive its own submission"
            body = page.inner_text("#results")
            assert "Availability checked" in body

            # 4. open a recommendation, 5. verify the trip detail
            page.locator(".card").first.click()
            page.wait_for_selector("text=Where you sleep")
            detail = page.inner_text("#results")
            assert "Day by day" in detail
            assert "Download GPX" in detail
            assert "about " in detail, "hiking days carry time estimates"
            nightrows = page.locator(".nightrow").count()
            assert nightrows >= 3, f"expected night+day rows, {nightrows}"

            # back to the cards, form restored
            page.click("#p_back2")
            page.wait_for_selector(".card")
            assert page.locator("#p_go").is_visible()

            browser.close()
        assert not errors, f"page JavaScript errors: {errors}"
        print(f"BROWSER OK: form submitted without destroying itself, "
              f"{cards} cards, detail verified, zero page errors")
    finally:
        server.should_exit = True


if __name__ == "__main__":
    main()
