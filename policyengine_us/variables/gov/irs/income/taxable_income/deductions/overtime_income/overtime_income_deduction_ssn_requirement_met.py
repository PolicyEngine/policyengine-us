from policyengine_us.model_api import *


class overtime_income_deduction_ssn_requirement_met(Variable):
    value_type = bool
    entity = TaxUnit
    label = "SSN requirement met for the overtime income deduction"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        joint = tax_unit("tax_unit_is_joint", period)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        eligible_head_or_spouse = person("has_valid_ssn", period) & head_or_spouse
        return where(
            joint,
            tax_unit.sum(eligible_head_or_spouse) == 2,
            tax_unit.any(eligible_head_or_spouse),
        )
