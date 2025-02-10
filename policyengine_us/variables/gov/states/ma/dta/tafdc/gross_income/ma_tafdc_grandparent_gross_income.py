from policyengine_us.model_api import *


class ma_tafdc_grandparent_gross_income(Variable):
    value_type = float
    unit = USD
    entity = TaxUnit
    label = "Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) grandparent earned income"
    definition_period = MONTH
    reference = (
        "https://www.masslegalservices.org/content/68-how-grandparent-income-counted-towards-baby-teen-parent"
    )
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ma.dta.tafdc.gross_income.deductions
        person = tax_unit.members
        is_grandparent = person("is_grandparent_of_filer_or_spouse", period)
        fpg = tax_unit("tax_unit_fpg", period)
        total_income = add(tax_unit, period, ["ma_tafdc_earned_income", "ma_tafdc_unearned_income"])
        teen_parent_present = tax_unit.any(
            person("ma_tafdc_eligible_teen_parent", period)
        )
        deduction = where(teen_parent_present, fpg * p.grandparent_income.percentage, 0)
        return tax_unit.sum(is_grandparent * max_(0, total_income - deduction))
