from policyengine_us.model_api import *


class mo_ccs_special_needs(Variable):
    value_type = bool
    entity = Person
    label = "Child with special needs for Missouri Child Care Subsidy"
    definition_period = MONTH
    defined_for = StateCode.MO
    reference = (
        "https://www.sos.mo.gov/CMSImages/AdRules/csr/current/5csr/5c25-200.pdf#page=2",
        "https://dese.mo.gov/sites/g/files/zuston521/files/media/pdf/2026/04/ACF-118%20CCDF%20FFY%202025-2027%20For%20Missouri%20-%20Approved%203.26.2026.pdf#page=26",
        "https://dese.mo.gov/sites/g/files/zuston521/files/media/pdf/2026/04/ACF-118%20CCDF%20FFY%202025-2027%20For%20Missouri%20-%20Approved%203.26.2026.pdf#page=52",
    )

    def formula(person, period, parameters):
        # "Child with special needs" (5 CSR 25-200.050(11)) covers six criteria:
        # (A) SSI receipt, (B) Missouri Department of Mental Health services,
        # (C) a verified physical or mental disability or delay, (D) a Protective
        # Service Child, (E) an Adoption Subsidy Child, or (F) a child under
        # court-ordered supervision. We model (A) via SSI receipt, (C) via
        # is_disabled, (D) via the protective-services category, and (F) via
        # is_under_court_supervision. (B), (E), and written verification remain
        # unmodeled. The same status drives the extended age ceiling
        # (mo_ccs_eligible_child), the market-rate +25%
        # special-needs rate column (mo_ccs_maximum_daily_benefit), and the
        # sliding-fee waiver (mo_ccs_copay), so all three stay consistent.
        # State Plan FFY 2025-2027 2.3.1(d) also lists a child under
        # court-ordered supervision, and 4.3.3(b)(ii) pays such children the
        # 25% special-needs rate differential. The Eligibility Policy Manual's
        # 6.7 lists only the SSI, mental-health, and disability criteria and
        # omits the court route; the rule and State Plan govern here.
        is_disabled = person("is_disabled", period.this_year)
        # A child receiving SSI is a child with special needs
        # (5 CSR 25-200.050(11)(A)).
        receives_ssi = (person("ssi", period) > 0) | person("receives_ssi", period)
        # A protective-services child is a child with special needs
        # (5 CSR 25-200.050(11)(D)).
        is_protective = person("mo_ccs_protective_services", period)
        under_court_supervision = person("is_under_court_supervision", period.this_year)
        return is_disabled | receives_ssi | is_protective | under_court_supervision
