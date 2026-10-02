"""Map a DPA against the Art. 28 rule library: FOUND / WEAK / MISSING, with clause cite and quote."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from .rules import RULES, TRANSFER_HINT, Rule

PARTICULARS = {
    r"subject[- ]matter": "subject-matter", r"duration": "duration", r"nature": "nature", r"nature and purpose|purposes? of (the )?processing": "purpose",
    r"(types|categories) of personal data": "types of personal data", r"categories of data subjects": "categories of data subjects"}
HOURS = {"hour": 1, "hours": 1, "day": 24, "days": 24, "calendar days": 24, "business days": 24 * 7 / 5, "business day": 24 * 7 / 5}


@dataclass
class Clause:
    cid: str
    text: str


@dataclass
class Result:
    rule: Rule
    status: str                       # FOUND | WEAK | MISSING | N/A
    cid: str = ""
    quote: str = ""
    why: list[str] = field(default_factory=list)


def clauses(text: str) -> list[Clause]:
    out = []
    for i, para in enumerate(p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()):
        m = re.match(r"^(\d+(?:\.\d+)*|Annex [IVX]+)\.?\s", para)
        out.append(Clause(m.group(1) if m else f"¶{i + 1}", " ".join(para.split())))
    return out


def _all(groups, text):
    return all(re.search(g, text, re.I) for g in groups)


def _quote(text, pattern, width=160):
    m = re.search(pattern, text, re.I)
    if not m:
        return text[:width]
    a = max(0, m.start() - 60)
    return ("…" if a else "") + text[a:a + width] + ("…" if a + width < len(text) else "")


def breach_deadline_hours(text: str) -> float | None:
    m = re.search(r"within\s+(?:\w+\s+\()?(\d+)\)?\s+(business days?|calendar days|days?|hours?)", text, re.I)
    return float(m.group(1)) * HOURS[m.group(2).lower()] if m else None


def evaluate(rule: Rule, cls: list[Clause], full: str) -> Result:
    if rule.rid == "transfers" and not TRANSFER_HINT.search(full):
        return Result(rule, "N/A", why=["no transfer outside the EEA mentioned"])
    if rule.whole_doc:
        missing = [g for g in rule.need if not re.search(g, full, re.I)]
        if not missing:
            return Result(rule, "FOUND", "whole document", _quote(full, rule.need[0]))
        why = ["missing: " + ", ".join(PARTICULARS[g] for g in missing)] if rule.rid == "particulars" \
            else ["transfers outside the EEA are mentioned but no SCCs / adequacy basis"]
        return Result(rule, "MISSING", why=why)

    hit = next((c for c in cls if _all(rule.need, c.text)), None)
    if hit is None:
        reds = [(c, pat, why) for c in cls for pat, why in rule.red if re.search(pat, c.text, re.I)]
        if rule.weak_substitute:
            pat, why = rule.weak_substitute
            sub = next((c for c in cls if re.search(pat, c.text, re.I)), None)
            if sub:
                return Result(rule, "WEAK", sub.cid, _quote(sub.text, pat), [why] + [w for _, _, w in reds])
        if reds:
            c, pat, why = reds[0]
            return Result(rule, "MISSING", c.cid, _quote(c.text, pat), ["required term absent, and: " + why])
        return Result(rule, "MISSING")
    res = Result(rule, "FOUND", hit.cid, _quote(hit.text, rule.need[-1]))
    for c in cls:                                   # red flags can sit in any clause on the same topic
        for pat, why in rule.red:
            if re.search(pat, c.text, re.I):
                res.status, res.cid, res.quote = "WEAK", c.cid, _quote(c.text, pat)
                res.why.append(why)
    if rule.rid == "breach":
        h = breach_deadline_hours(hit.text)
        if h is not None and h > 48:
            res.status = "WEAK"
            res.why.append(f"notice within ~{h:.0f} h — leaves Customer little or none of its 72 h (Art. 33) to notify the authority")
    return res


@dataclass
class Report:
    name: str
    results: list[Result]

    @property
    def counts(self):
        c = {"FOUND": 0, "WEAK": 0, "MISSING": 0, "N/A": 0}
        for r in self.results:
            c[r.status] += 1
        return c


def check(path: Path) -> Report:
    text = path.read_text(encoding="utf-8")
    cls = clauses(text)
    return Report(path.stem, [evaluate(r, cls, text) for r in RULES])
