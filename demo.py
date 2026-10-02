"""python demo.py [dpa.md ...] -> scorecard for each DPA, out/<name>_memo.md, out/scorecard.html"""
from __future__ import annotations

import sys
import time
from html import escape
from pathlib import Path

from dpacheck.check import check

HERE = Path(__file__).parent
COL = {"FOUND": "ok", "WEAK": "warn", "MISSING": "bad", "N/A": "mut"}
CSS = """
:root{--bg:#fbfaf7;--fg:#1d1c19;--mut:#6d6a63;--line:#e4e1da;--card:#fff;--ok:#1f6f4a;--warn:#9a5b00;--bad:#b3261e}
@media (prefers-color-scheme:dark){:root{--bg:#131312;--fg:#ecebe6;--mut:#9b988f;--line:#2c2b28;--card:#1b1b19;--ok:#58c08d;--warn:#e2ad55;--bad:#ef7a66}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.5 system-ui,sans-serif}
main{max-width:1240px;margin:0 auto;padding:30px 16px}h1{font-size:25px;margin:0}h2{font-size:17px;margin:26px 0 10px}.mut{color:var(--mut)}
.scroll{overflow-x:auto}table{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line)}
th,td{text-align:left;padding:8px 9px;border-bottom:1px solid var(--line);vertical-align:top}th{font-size:11px;text-transform:uppercase;color:var(--mut)}
.ok{color:var(--ok)}.warn{color:var(--warn)}.bad{color:var(--bad)}.s{font:700 12px ui-monospace,monospace}
.cell{min-width:150px}.q{font:12px Georgia,serif;color:var(--mut)}
"""


def memo(r) -> str:
    c = r.counts
    lines = [f"# DPA review — {r.name}", f"GDPR Art. 28 + Chapter V · {c['FOUND']} found · {c['WEAK']} weak · {c['MISSING']} missing", ""]
    for status in ("MISSING", "WEAK"):
        items = [x for x in r.results if x.status == status]
        if items:
            lines.append(f"## {status.title()}")
            for x in items:
                lines.append(f"- **{x.rule.title}** ({x.rule.article})" + (f", §{x.cid}" if x.cid else ""))
                for w in x.why:
                    lines.append(f"  - {w}")
                if x.quote:
                    lines.append(f"  - Current text: “{x.quote}”")
                lines.append(f"  - Proposed: {x.rule.fix}")
            lines.append("")
    lines.append("## Found\n" + "\n".join(f"- {x.rule.title} ({x.rule.article}) §{x.cid}" for x in r.results if x.status == "FOUND"))
    return "\n".join(lines)


def main():
    files = [Path(a) for a in sys.argv[1:]] or sorted((HERE / "samples").glob("*.md"))
    t0 = time.perf_counter()
    reports = [check(f) for f in files]
    ms = (time.perf_counter() - t0) * 1000
    out = HERE / "out"
    out.mkdir(exist_ok=True)
    for r in reports:
        (out / f"{r.name}_memo.md").write_text(memo(r), encoding="utf-8")
        c = r.counts
        print(f"\n{r.name}: {c['FOUND']} found · {c['WEAK']} weak · {c['MISSING']} missing")
        for x in r.results:
            if x.status in ("WEAK", "MISSING"):
                print(f"  {x.status:7} {x.rule.article:24} {x.rule.title[:52]:52} " + ("§" + x.cid if x.cid else "") +
                      (f" — {x.why[0][:70]}" if x.why else ""))
    print(f"\nchecked {len(reports)} DPAs in {ms:.0f} ms · memos in out/")

    head = "".join(f"<th>{escape(r.name)}</th>" for r in reports)
    rows = ""
    for i, rule in enumerate(reports[0].results):
        cells = ""
        for r in reports:
            x = r.results[i]
            why = "".join(f"<div>{escape(w)}</div>" for w in x.why)
            q = f"<div class=q>“{escape(x.quote[:110])}”</div>" if x.status != "FOUND" and x.quote else ""
            cells += f"<td class=cell><span class='s {COL[x.status]}'>{x.status}</span>{' §' + escape(x.cid) if x.cid and x.cid != 'whole document' else ''}{why}{q}</td>"
        rows += f"<tr><td><b>{escape(rule.rule.title)}</b><div class=mut>{escape(rule.rule.article)}</div></td>{cells}</tr>"
    html = f"""<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>DPA Article 28 Check</title><style>{CSS}</style></head><body><main>
<h1>DPA check — GDPR Art. 28 + Chapter V</h1>
<div class=mut>3 synthetic vendor DPAs · every flag cites its article and comes with fix language in the memo · {ms:.0f} ms · unofficial prototype by Kushagra Pratap Singh</div>
<h2>Scorecard</h2><div class=scroll><table><tr><th>Requirement</th>{head}</tr>{rows}</table></div>
</main></body></html>"""
    (out / "scorecard.html").write_text(html, encoding="utf-8")


if __name__ == "__main__":
    main()
