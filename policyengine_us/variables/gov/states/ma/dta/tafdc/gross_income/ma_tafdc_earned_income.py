from policyengine_us.model_api import *


class ma_tafdc_earned_income(Variable):
    value_type = float
    unit = USD
    entity = Person
    label = "Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) earned income"
    definition_period = YEAR
    reference = (
        "https://www.masslegalservices.org/content/62-what-income-counted"
    )
    defined_for = StateCode.MA

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ma.dta.tafdc.gross_income
        total_earned_income = add(person, period, p.earned)
        flat_disregard = (
            p.deductions.earned_income_disregard.flat * MONTHS_IN_YEAR
        )
        reduced_income = (
            total_earned_income - flat_disregard
        ) * p.deductions.earned_income_disregard.percentage
        dependent_care_deduction = person("ma_tafdc_dependent_care_deduction", period)
        # The income of grandparents is computed separately
        is_grandparent = person("is_grandparent_of_filer_or_spouse", period)
        return max_(0, reduced_income - dependent_care_deduction) * ~is_grandparent


# TODO: 100% disregard for the first 6 months of income
