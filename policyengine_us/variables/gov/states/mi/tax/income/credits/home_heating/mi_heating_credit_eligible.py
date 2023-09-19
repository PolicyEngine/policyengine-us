from policyengine_us.model_api import *


class mi_heating_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible Household for the Michigan heating credit"
    definition_period = YEAR
    defined_for = StateCode.MI

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        is_not_dsi = ~tax_unit("dsi", period)
        is_not_ft_student = ~person("is_full_time_student", period)
        is_head = person("is_tax_unit_head", period)
        is_spouse = person("is_tax_unit_spouse", period)
        head_or_spouse = is_head | is_spouse

        return is_not_dsi & tax_unit.any(is_not_ft_student & head_or_spouse)
