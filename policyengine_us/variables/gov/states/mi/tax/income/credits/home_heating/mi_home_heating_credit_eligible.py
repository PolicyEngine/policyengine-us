from policyengine_us.model_api import *


class mi_home_heating_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Michigan heating credit"
    definition_period = YEAR
    defined_for = StateCode.MI

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        dependent_elsewhere = person(
            "claimed_as_dependent_on_another_return", period
        )
        ft_student = person("is_full_time_student", period)

        return ~tax_unit.any(ft_student & dependent_elsewhere)
