from pathlib import Path

import pytest

from dpacheck.check import breach_deadline_hours, check, clauses, evaluate
from dpacheck.rules import RULES

S = Path(__file__).resolve().parents[1] / "samples"
R = {r.rid: r for r in RULES}


def status(report):
    return {x.rule.rid: x.status for x in report.results}


def test_good_dpa_is_clean():
    assert set(status(check(S / "lumen_analytics_dpa.md")).values()) == {"FOUND"}


def test_mediocre_dpa():
    st = status(check(S / "brightdesk_dpa.md"))
    assert {k for k, v in st.items() if v == "WEAK"} == {"sub_authorisation", "breach", "deletion", "audit"}
    assert {k for k, v in st.items() if v == "MISSING"} == {"confidentiality", "dpia"}


def test_bad_dpa():
    st = status(check(S / "quickform_dpa.md"))
    assert st["transfers"] == "MISSING" and st["instructions"] == "MISSING" and st["security"] == "WEAK"
    assert sum(v == "FOUND" for v in st.values()) == 0


def test_every_flag_cites_an_article_and_fix():
    for f in S.glob("*.md"):
        for x in check(f).results:
            assert x.rule.article and x.rule.fix


@pytest.mark.parametrize("text,hours", [
    ("notify within five (5) business days", 168), ("within 24 hours after becoming aware", 24),
    ("within 3 days", 72), ("without undue delay", None)])
def test_breach_deadline(text, hours):
    assert breach_deadline_hours(text) == hours


def test_soc2_only_audit_is_weak():
    cls = clauses("1. Audits. Customer may audit once a year. The SOC 2 report shall satisfy audit rights in lieu of inspection.")
    assert evaluate(R["audit"], cls, "").status == "WEAK"


def test_transfers_not_applicable_without_third_country():
    text = "1. Location. All data is stored in Frankfurt."
    assert evaluate(R["transfers"], clauses(text), text).status == "N/A"


def test_negation_free_instruction_clause_found():
    cls = clauses("2. Instructions. Processor shall process Personal Data only on documented instructions from Customer.")
    assert evaluate(R["instructions"], cls, "").status == "FOUND"
