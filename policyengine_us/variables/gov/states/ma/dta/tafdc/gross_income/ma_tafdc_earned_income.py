from policyengine_us.model_api import *


class ma_tafdc_earned_income(Variable):
    value_type = float
    unit = USD
    entity = TaxUnit
    label = "Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) earned income"
    definition_period = YEAR
    reference = (
        "https://www.masslegalservices.org/content/62-what-income-counted"
    )
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ma.dta.tafdc.gross_income
        total_earned_income = add(tax_unit, period, p.earned)
        monthly_earned_income = total_earned_income / MONTHS_IN_YEAR
        # The first 6 months of income are disregarded at a 100% rate

        reduced_income = (
            total_earned_income - p.earned_income_disregard.flat
        ) * p.earned_income_disregard.percentage
        dependent_care_deduction = tax_unit.sum(
            tax_unit.members("ma_tafdc_dependent_care_deduction", period)
        )
        return max_(0, reduced_income - dependent_care_deduction)


# TODO: 100% disregard for the first 6 months of income
