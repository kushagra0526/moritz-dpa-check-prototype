# DPA review — brightdesk_dpa
GDPR Art. 28 + Chapter V · 7 found · 4 weak · 2 missing

## Missing
- **Personnel bound by confidentiality** (Art. 28(3)(b))
  - Proposed: Processor shall ensure that persons authorised to process Personal Data have committed themselves to confidentiality or are under an appropriate statutory obligation of confidentiality.
- **Assists with DPIAs and prior consultation** (Art. 28(3)(f) / Arts. 35–36)
  - Proposed: Processor shall provide reasonable assistance with data protection impact assessments and prior consultations with supervisory authorities under Articles 35 and 36 GDPR.

## Weak
- **Sub-processors only with prior written authorisation, with notice and a right to object** (Art. 28(2) / 28(3)(d)), §4
  - sub-processors can change with no right for Customer to object
  - changes only posted / without notice — controller can't realistically object
  - Current text: “4. Sub-processors. Customer provides general authorisation for Brightdesk to engage sub-processors. Brightdesk will update the list of sub-processors posted on …”
  - Proposed: Processor shall give Customer at least 30 days' prior written notice of any new sub-processor; Customer may object on reasonable grounds, in which case the parties shall discuss in good faith and Customer may terminate the affected Services.
- **Breach notification without undue delay (Customer has 72 h to notify the authority)** (Art. 28(3)(f) / Art. 33), §6
  - notice within ~168 h — leaves Customer little or none of its 72 h (Art. 33) to notify the authority
  - Current text: “6. Security incidents. Brightdesk will notify Customer of a breach affecting Customer Personal Data within five (5) business days of confirming the incident.”
  - Proposed: Processor shall notify Customer without undue delay, and in any event within 48 hours, after becoming aware of a Personal Data Breach, with the information required by Article 33(3).
- **Deletes or returns all personal data at the end of the services** (Art. 28(3)(g)), §7
  - retention carve-out with no time limit (backups/business purposes)
  - Current text: “…l delete Customer Personal Data, except that Brightdesk may retain copies in backups and archives in accordance with its standard practices.”
  - Proposed: At the end of the Services, Processor shall at Customer's choice delete or return all Personal Data and delete existing copies (including backups within 30 days), unless Union or Member State law requires storage.
- **Makes information available and allows audits, including inspections** (Art. 28(3)(h)), §8
  - audit right limited to a third-party report — Art. 28(3)(h) requires allowing audits, including inspections
  - Current text: “…tdesk's compliance once per year. Brightdesk's then-current SOC 2 Type II report shall satisfy Customer's audit rights in lieu of any on-site inspection.”
  - Proposed: Processor shall make available all information necessary to demonstrate compliance and allow for and contribute to audits, including inspections, by Customer or an auditor it mandates; third-party reports may be provided first but do not replace this right.

## Found
- Subject-matter, duration, nature, purpose, data types, data subject categories (Art. 28(3)) §whole document
- Processes only on documented instructions (Art. 28(3)(a)) §2
- Tells the controller if an instruction infringes data protection law (Art. 28(3) final subpara.) §2
- Article 32 security measures (Art. 28(3)(c) / Art. 32) §3
- Same obligations flowed down; processor remains fully liable (Art. 28(4)) §4
- Assists with data subject rights requests (Art. 28(3)(e)) §5
- Transfers outside the EEA covered by SCCs / adequacy (Chapter V (Arts. 44–46)) §whole document