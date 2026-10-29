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
        # Rhode Island's 12-month continuation adds to the state's day-count
        # postpartum period (postpartum_coverage); it does not replace it.
        # Only a Medicaid pregnancy keeps the pregnancy group (SHO 21-007 Q6).
        coverage = person("ri_pregnancy_coverage", period)
        ri_postpartum_eligible = person(
            "ri_medicaid_postpartum_eligible", period.first_month
        ) & (coverage == coverage.possible_values.MEDICAID)
        return (
            is_pregnant
            | (days_postpartum < max_postpartum_days)
            | ri_postpartum_eligible
        )
