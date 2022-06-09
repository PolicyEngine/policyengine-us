from openfisca_us.model_api import *


class is_pregnant_for_medicaid_nfc(Variable):
    value_type = bool
    entity = Person
    label = "Medicaid pregnant non-financial criteria"
    definition_period = YEAR

    def formula(person, period, parameters):
        ma = parameters(period).hhs.medicaid.eligibility.categories.pregnant
        is_pregnant = person("is_pregnant", period)
        days_postpartum = person("count_days_postpartum", period)
        state = person.household("state_code_str", period)
        max_postpartum_days = ma.postpartum_coverage[state]
        return is_pregnant | (days_postpartum < max_postpartum_days)
