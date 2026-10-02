"""GDPR Art. 28 (+ Chapter V) rule library. Each rule cites its article and carries fix language.

A rule is FOUND if some clause matches every `need` group (each group = alternatives), WEAK if found but a
red flag fires (or a weak substitute is present), MISSING otherwise. Patterns are regexes, case-insensitive.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class Rule:
    rid: str
    article: str
    title: str
    need: list[str]
    red: list[tuple[str, str]] = field(default_factory=list)     # (pattern, why it's weak)
    weak_substitute: tuple[str, str] | None = None              # pattern that counts as WEAK if `need` is absent
    fix: str = ""
    whole_doc: bool = False                                       # evaluate on the whole text, not one clause


SUB = r"sub-?processors?"
RULES = [
    Rule("particulars", "Art. 28(3)", "Subject-matter, duration, nature, purpose, data types, data subject categories",
         need=[r"subject[- ]matter", r"duration", r"nature", r"nature and purpose|purposes? of (the )?processing", r"(types|categories) of personal data", r"categories of data subjects"],
         whole_doc=True,
         fix="Add an Annex describing the subject-matter, duration, nature and purpose of processing, the types of personal data and the categories of data subjects."),
    Rule("instructions", "Art. 28(3)(a)", "Processes only on documented instructions",
         need=[r"\b(only|solely)\b", r"documented instructions|written instructions"],
         red=[(r"improve (our|its) (services|products|models)|for (its|our) own (business )?purposes",
               "allows processing for the vendor's own purposes — outside the controller's instructions")],
         fix="Processor shall process Personal Data only on documented instructions from Customer, including with regard to transfers, unless required by Union or Member State law."),
    Rule("infringing", "Art. 28(3) final subpara.", "Tells the controller if an instruction infringes data protection law",
         need=[r"instruction", r"infring|violat", r"inform|notify"],
         fix="Processor shall immediately inform Customer if, in its opinion, an instruction infringes the GDPR or other Union or Member State data protection provisions."),
    Rule("confidentiality", "Art. 28(3)(b)", "Personnel bound by confidentiality",
         need=[r"confidential", r"personnel|employees|staff|persons authori[sz]ed"],
         fix="Processor shall ensure that persons authorised to process Personal Data have committed themselves to confidentiality or are under an appropriate statutory obligation of confidentiality."),
    Rule("security", "Art. 28(3)(c) / Art. 32", "Article 32 security measures",
         need=[r"article 32|technical and organi[sz]ational measures"],
         weak_substitute=(r"industry[- ]standard (security|safeguards)", "only 'industry standard security' — no Art. 32 technical and organisational measures described"),
         fix="Processor shall implement the technical and organisational measures set out in Annex II, which meet the requirements of Article 32 GDPR."),
    Rule("sub_authorisation", "Art. 28(2) / 28(3)(d)", "Sub-processors only with prior written authorisation, with notice and a right to object",
         need=[SUB, r"authori[sz]|consent|approv", r"object"],
         weak_substitute=(SUB, "sub-processors can change with no right for Customer to object"),
         red=[(r"posted on (our|its) website|without (prior )?notice", "changes only posted / without notice — controller can't realistically object")],
         fix="Processor shall give Customer at least 30 days' prior written notice of any new sub-processor; Customer may object on reasonable grounds, in which case the parties shall discuss in good faith and Customer may terminate the affected Services."),
    Rule("flow_down", "Art. 28(4)", "Same obligations flowed down; processor remains fully liable",
         need=[SUB, r"same|equivalent|no less protective", r"liable"],
         fix="Processor shall impose on each sub-processor the same data protection obligations as in this DPA and shall remain fully liable to Customer for the sub-processor's performance."),
    Rule("dsr", "Art. 28(3)(e)", "Assists with data subject rights requests",
         need=[r"data subjects?", r"request|rights", r"assist"],
         fix="Processor shall assist Customer by appropriate technical and organisational measures in fulfilling its obligation to respond to requests from data subjects exercising their rights under Chapter III GDPR."),
    Rule("breach", "Art. 28(3)(f) / Art. 33", "Breach notification without undue delay (Customer has 72 h to notify the authority)",
         need=[r"breach", r"notif"],
         red=[(r"commercially reasonable (time|period)", "no fixed deadline ('commercially reasonable time')")],
         fix="Processor shall notify Customer without undue delay, and in any event within 48 hours, after becoming aware of a Personal Data Breach, with the information required by Article 33(3)."),
    Rule("dpia", "Art. 28(3)(f) / Arts. 35–36", "Assists with DPIAs and prior consultation",
         need=[r"impact assessment|dpia", r"assist|cooperat"],
         fix="Processor shall provide reasonable assistance with data protection impact assessments and prior consultations with supervisory authorities under Articles 35 and 36 GDPR."),
    Rule("deletion", "Art. 28(3)(g)", "Deletes or returns all personal data at the end of the services",
         need=[r"delete|return", r"terminat|expir|end of"],
         red=[(r"(retain|keep).{0,80}(backups?|archives?).{0,80}(standard practice|business|indefinite)|for (its|our) legitimate business purposes",
               "retention carve-out with no time limit (backups/business purposes)")],
         fix="At the end of the Services, Processor shall at Customer's choice delete or return all Personal Data and delete existing copies (including backups within 30 days), unless Union or Member State law requires storage."),
    Rule("audit", "Art. 28(3)(h)", "Makes information available and allows audits, including inspections",
         need=[r"audit|inspection"],
         red=[(r"(soc ?2|iso ?27001).{0,120}(in lieu|instead|shall satisfy|sole|exclusive|only)|(sole|only|exclusive).{0,80}(soc ?2|iso ?27001)",
               "audit right limited to a third-party report — Art. 28(3)(h) requires allowing audits, including inspections")],
         fix="Processor shall make available all information necessary to demonstrate compliance and allow for and contribute to audits, including inspections, by Customer or an auditor it mandates; third-party reports may be provided first but do not replace this right."),
    Rule("transfers", "Chapter V (Arts. 44–46)", "Transfers outside the EEA covered by SCCs / adequacy",
         need=[r"standard contractual clauses|\bsccs?\b|adequacy decision|data privacy framework"],
         whole_doc=True,
         fix="Where Personal Data is transferred outside the EEA, the parties incorporate the EU Standard Contractual Clauses (Module 2/3) as set out in Annex III (UK: the IDTA or UK Addendum)."),
]

TRANSFER_HINT = re.compile(r"united states|\bus\b|india|third countr|outside the (eea|european economic area|eu)", re.I)
