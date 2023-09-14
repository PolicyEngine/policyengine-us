from policyengine_us.model_api import *


class mi_heating_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Michigan heating credit can be claimed"
    definition_period = YEAR
    defined_for = StateCode.MI

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        is_not_dsi = ~tax_unit("dsi",period)
        is_not_ft_student = ~person("is_full_time_student",period)
        
        return  is_not_dsi & is_not_ft_student
