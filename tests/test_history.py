"""M8 invariants: the log grows on every record, survives junk, and the
demand derivation math is right on synthetic rows."""
import sys, os, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from switchback import history


def main():
    tmp = os.path.join(tempfile.mkdtemp(), "h.sqlite")
    history.set_db_path(tmp)
    per = {"2099-09-22": {"remaining": 0, "total": 4},
           "2099-09-23": {"remaining": 2, "total": 4}}
    assert history.record_month("4675321", "DIV1", per) == 2
    assert history.record_month("4675321", "DIV1", per) == 2
    n = history._db().execute("SELECT COUNT(*) FROM scans").fetchone()[0]
    assert n == 4, "log must grow on every run"
    assert history.record_month("4675321", "DIV1", {}) == 0

    for _ in range(15):
        history.record_month("4675321", "DIV1", per)
    db = history._db()
    full, total = db.execute(
        "SELECT SUM(CASE WHEN remaining <= 0 THEN 1 ELSE 0 END), COUNT(*) "
        "FROM scans WHERE total > 0 AND date >= '2098-01-01'").fetchone()
    assert total >= 30 and abs(full / total - 0.5) < 1e-9, \
        "fullness proxy must be exactly half on this synthetic mix"
    import tempfile as _tf
    pdi_out = os.path.join(_tf.mkdtemp(), "pdi.json")
    path, n = history.derive_pdi(min_samples=30, out_path=pdi_out)
    import json as _json
    pdi = _json.load(open(path))
    entry = list(pdi["glacier"].values())[0]
    assert n == 1 and entry["pdi"] == 50 and entry["samples"] >= 30
    assert entry["weekend_premium"] is None, "premium needs 10+ weekend samples"

    history.set_db_path(os.environ.get("SWITCHBACK_HISTORY_PATH",
                                       history.DB_PATH))
    print(f"HISTORY OK: {n} rows after two scans, fullness 0.5 exact, PDI 50 with honest null components")


if __name__ == "__main__":
    main()
