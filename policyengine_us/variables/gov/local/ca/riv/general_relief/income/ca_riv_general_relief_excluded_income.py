from policyengine_us.model_api import *


class ca_riv_general_relief_excluded_income(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Income amount excluded from ineligible household members due to proration under Riverside County General Relief Program"
    definition_period = MONTH
    defined_for = "ca_riv_general_relief_ineligible_person"

    def formula(person, period, parameters):
        income = person(
            "ca_riv_general_relief_countable_income_person", period
        )
        spm_unit = person.spm_unit
        needs_unit_size = spm_unit("spm_unit_size", period)
        budget_unit_size = spm_unit(
            "ca_riv_general_relief_budget_unit_size", period
        )
        exclusion_rate = (needs_unit_size - budget_unit_size) / needs_unit_size
        return exclusion_rate * income
