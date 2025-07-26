from policyengine_us.model_api import *


class pr_education_deduction_beneficiary_count(Variable):
    value_type = float
    entity = TaxUnit
    label = "Puerto Rico education contribution deduction beneficiary count"
    unit = USD
    definition_period = YEAR
    reference = "https://law.justia.com/codes/puerto-rico/title-thirteen/subtitle-17/part-ii/chapter-1005/subchapter-c/30135/"  # (8)
    defined_for = StateCode.PR

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.territories.pr.tax.income.taxable_income.deductions.education
        person = tax_unit.members
        is_dependent = person("is_tax_unit_dependent", period)
        age_eligible = person("age", period) < p.age_threshold
        return tax_unit.sum(is_dependent & age_eligible)
