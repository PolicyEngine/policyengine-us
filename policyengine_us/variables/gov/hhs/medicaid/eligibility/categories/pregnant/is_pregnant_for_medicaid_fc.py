from policyengine_us.model_api import *


class is_pregnant_for_medicaid_fc(Variable):
    value_type = bool
    entity = Person
    label = "Medicaid pregnant financial criteria"
    definition_period = YEAR
    reference = (
        # 42 CFR 435.116(b): pregnant women with household income at or below the
        # state's income standard.
        "https://www.law.cornell.edu/cfr/text/42/435.116",
        # WIC § 15832(a)(1)(B): California's Medi-Cal Access Program begins above
        # the pregnancy Medi-Cal limit, so income exactly at the limit stays in
        # Medi-Cal.
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=WIC&sectionNum=15832.",
    )

    def formula(person, period, parameters):
        ma = parameters(period).gov.hhs.medicaid.eligibility.categories.pregnant
        income = person("medicaid_income_level", period)
        state = person.household("state_code_str", period)
        income_limit = ma.income_limit[state]
        # California's ceiling is inclusive. Compare at the stored income ratio's
        # precision so exactly 213% is not rejected by float32 rounding.
        ca_eligible = income <= np.asarray(income_limit, dtype=income.dtype)
        return where(state == "CA", ca_eligible, income < income_limit)
