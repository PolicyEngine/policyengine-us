from policyengine_us.model_api import *


class is_pregnant_for_medicaid_nfc(Variable):
    value_type = bool
    entity = Person
    label = "Medicaid pregnant non-financial criteria"
    definition_period = YEAR

    def formula(person, period, parameters):
        ma = parameters(period).gov.hhs.medicaid.eligibility.categories.pregnant
        is_pregnant = person("is_pregnant", period)
        days_postpartum = person("count_days_postpartum", period)
        state = person.household("state_code_str", period)
        max_postpartum_days = ma.postpartum_coverage[state]
        ri = parameters(period).gov.states.ri.eohhs.medicaid
        ri_continuation_applies = (state == "RI") & (ri.postpartum_coverage_months > 0)
        postpartum_eligible = where(
            ri_continuation_applies,
            person("ri_medicaid_postpartum_eligible", period.first_month),
            days_postpartum < max_postpartum_days,
        )
        return is_pregnant | postpartum_eligible
