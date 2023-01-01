from policyengine_us.model_api import *


class spouse_earned(Variable):
    value_type = float
    entity = TaxUnit
    label = "Spouse's earnings"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        earned_income = max_(0, person("earned_income", period))
        se_tax_ded = person("self_employment_tax_ald_person", period)
        is_spouse = person("is_tax_unit_spouse", period)
        return tax_unit.sum(is_spouse * max_(0, earned_income - se_tax_ded))
