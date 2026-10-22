from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicaid.income.medicaid_income_level import (
    medicaid_income_eligible,
)


class is_pregnant_for_medicaid_fc(Variable):
    value_type = bool
    entity = Person
    label = "Medicaid pregnant financial criteria"
    definition_period = YEAR
    reference = (
        # 42 CFR 435.116(b): pregnant women with household income at or below the
        # state's income standard.
        "https://www.law.cornell.edu/cfr/text/42/435.116",
        # WIC § 15832(a)(1)(B): California's Medi-Cal Access Program covers
        # household income "above 208 percent" but "not exceed[ing] 317
        # percent" of the FPL (213% and 322% after the 5 percentage point MAGI
        # disregard), so income exactly at the pregnancy Medi-Cal limit stays in
        # Medi-Cal. The section-level URL returns a version picker; this link
        # renders the full chapter text.
        "https://leginfo.legislature.ca.gov/faces/codes_displayText.xhtml?lawCode=WIC&division=9.&title=&part=3.3.&chapter=2.&article=",
        # R.I. Gen. Laws § 42-12.3-3(g): people eligible for Medicaid or CHIP
        # while pregnant keep full Medicaid through the postpartum period.
        "https://webserver.rilegislature.gov/Statutes/TITLE42/42-12.3/42-12.3-3.htm",
        "https://rules.sos.ri.gov/regulations/part/210-30-00-1",
    )

    def formula(person, period, parameters):
        ma = parameters(period).gov.hhs.medicaid.eligibility.categories.pregnant
        state = person.household("state_code_str", period)
        income_limit = ma.income_limit[state]
        ri = parameters(period).gov.states.ri.eohhs.medicaid
        postpartum = ~person("is_pregnant", period) & (
            person("count_days_postpartum", period) < ma.postpartum_coverage[state]
        )
        # Rhode Island covers insured pregnant people through Medicaid at its
        # CHIP pregnancy ceiling. The same ceiling approximates prior pregnancy
        # eligibility for extended postpartum coverage using current income.
        ri_higher_limit = (state == "RI") & (
            person("ri_medicaid_has_third_party_coverage", period)
            | (ri.extended_postpartum_coverage & postpartum)
        )
        chip_income_limit = parameters(period).gov.hhs.chip.pregnant.income_limit[state]
        income_limit = where(ri_higher_limit, chip_income_limit, income_limit)
        return medicaid_income_eligible(person, period, parameters, income_limit)
