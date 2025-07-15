from policyengine_us.model_api import *


class pr_education_deduction_beneficiary_count(Variable):
    value_type = float
    entity = TaxUnit
    label = "Puerto Rico education contribution deduction beneficiary count"
    unit = USD
    definition_period = YEAR
    reference = ""  
    defined_for = StateCode.PR

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.territories.pr.tax.income.taxable_income.deductions.education
        person = tax_unit.members(period)
        age = person("age", period)
        return tax_unit.sum(
            person("is_tax_unit_dependent", period) & (age < p.age_threshold)
        )