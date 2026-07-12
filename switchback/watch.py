"""
switchback.watch: M9 watch mode and Telegram alerts.

WatchState is a pure state machine so the alert logic is testable
without a network: feed it snapshots ({(division_id, date): remaining}),
get back the alerts that are due. Rules per ROADMAP:

  transition  a cell alerts only on Full-to-Reservable movement:
              previous remaining below party, current at or above it,
              with real quota (rec.gov negative remaining clamps to 0
              upstream in fetch_availability)
  flicker     an opening must persist across one re-check before it
              alerts; a one-poll blip never fires
  exactly     one alert per opening; the cell must close again before
              it can ever re-alert

The loop wrapper polls with a jittered interval, persists state to
parks/.watch_state.json so restarts do not re-alert, and sends through
Telegram (token and chat id from TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID
env vars, else telegram.json at the repo root; see
telegram.json.example). Every poll also feeds the M8 history log for
free, since it rides the same fetch choke point.
"""
import json
import os
import random
import time
import urllib.parse
import urllib.request
from datetime import date, timedelta

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_PATH = os.path.join(_ROOT, "parks", ".watch_state.json")
TELEGRAM_PATH = os.path.join(_ROOT, "telegram.json")


class WatchState:
    """cells: {key: phase} where phase is 'closed', 'candidate', 'alerted'."""

    def __init__(self, party=1, cells=None):
        self.party = party
        self.cells = cells or {}

    def observe(self, snapshot):
        """One poll's readings. Returns [key, ...] due for alert now."""
        due = []
        for key, remaining in snapshot.items():
            open_now = remaining is not None and remaining >= self.party
            phase = self.cells.get(key, "closed")
            if not open_now:
                self.cells[key] = "closed"
            elif phase == "closed":
                self.cells[key] = "candidate"
            elif phase == "candidate":
                self.cells[key] = "alerted"
                due.append(key)
        return due

    def to_json(self):
        return {"party": self.party,
                "cells": {f"{k[0]}|{k[1]}": v for k, v in self.cells.items()}}

    @classmethod
    def from_json(cls, d):
        cells = {tuple(k.split("|", 1)): v
                 for k, v in (d.get("cells") or {}).items()}
        return cls(party=d.get("party", 1), cells=cells)


# ------------------------------ telegram ----------------------------------
def telegram_config():
    tok = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat = os.environ.get("TELEGRAM_CHAT_ID")
    if tok and chat:
        return tok, chat
    try:
        with open(TELEGRAM_PATH) as fh:
            d = json.load(fh)
        return d.get("bot_token"), d.get("chat_id")
    except (OSError, ValueError):
        return None, None


def send_telegram(text):
    tok, chat = telegram_config()
    if not tok or not chat:
        raise RuntimeError("no Telegram config: set TELEGRAM_BOT_TOKEN and "
                           "TELEGRAM_CHAT_ID, or copy telegram.json.example "
                           "to telegram.json and fill it in")
    data = urllib.parse.urlencode({"chat_id": chat, "text": text}).encode()
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{tok}/sendMessage", data=data)
    with urllib.request.urlopen(req, timeout=30) as r:
        json.load(r)


def alert_text(g, div_id, ds, remaining):
    name = next((n["name"] for n in g.nodes.values()
                 if n.get("division_id") == div_id), div_id)
    url = (f"https://www.recreation.gov/permits/{g.park['permit_id']}"
           f"/registration/detailed-availability?date={ds}")
    return (f"Switchback: {name} opened for {ds} in {g.park['name']} "
            f"({remaining} left). Book: {url}")


# ------------------------------ the loop -----------------------------------
def _load_state(party):
    try:
        with open(STATE_PATH) as fh:
            st = WatchState.from_json(json.load(fh))
        st.party = party
        return st
    except (OSError, ValueError):
        return WatchState(party=party)


def _save_state(st):
    try:
        with open(STATE_PATH, "w") as fh:
            json.dump(st.to_json(), fh)
    except OSError:
        pass


def run_watch(g, div_ids, start, end, party=1, interval=300, once=False,
              no_send=False, inject=None, fetch_fn=None, sleep_fn=time.sleep):
    """Poll until interrupted. inject='DIV:YYYY-MM-DD' manufactures a
    Full-to-Reservable transition on the first two polls (done-criterion:
    exactly one message). fetch_fn is injectable for tests."""
    from .solver import fetch_availability
    fetch = fetch_fn or (lambda: fetch_availability(
        g.park["permit_id"], div_ids, start, end))
    st = _load_state(party)
    sent = 0
    cycle = 0
    while True:
        cycle += 1
        av = fetch()
        snapshot = {}
        for div, days in av.items():
            for ds, rem in days.items():
                if start.isoformat() <= ds <= end.isoformat():
                    snapshot[(div, ds)] = rem
        if inject:
            div, ds = inject.split(":", 1)
            snapshot[(div, ds)] = party  # manufactured opening, persists
        due = st.observe(snapshot)
        _save_state(st)
        for div, ds in due:
            msg = alert_text(g, div, ds, snapshot[(div, ds)])
            if no_send:
                print(f"WOULD SEND: {msg}")
            else:
                send_telegram(msg)
            sent += 1
        print(f"cycle {cycle}: {len(snapshot)} cells watched, "
              f"{len(due)} alert(s), {sent} sent total", flush=True)
        if once and cycle >= (2 if inject else 1):
            return sent
        sleep_fn(interval * random.uniform(0.8, 1.2))
