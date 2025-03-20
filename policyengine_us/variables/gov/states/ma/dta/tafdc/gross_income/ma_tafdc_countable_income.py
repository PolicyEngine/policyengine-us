from policyengine_us.model_api import *


class ma_tafdc_countable_income(Variable):
    value_type = float
    unit = USD
    entity = Person
    label = "Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) countable income"
    definition_period = YEAR
    reference = "https://www.masslegalservices.org/content/75-how-much-will-you-get-each-month"
    defined_for = StateCode.MA

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.ma.dta.tafdc.gross_income.deductions.earned_income_disregard
        total_earned_income = add(person, period, p.earned)
        # fully disregard for 6 months
        monthly_income = total_earned_income / MONTHS_IN_YEAR
        fully_disregard_eligible = person.spm_unit(
            "ma_tafdc_eligible_fully_disregard", period
        )
        fully_disregard = (
            monthly_income - monthly_income * p.fully_disregard.percentage
        ) * p.fully_disregard.applicable_months
        remaining_months = MONTHS_IN_YEAR - p.fully_disregard.applicable_months
        # then $200 flat disregard and 50% disregard for the rest
        flat_disregard = p.flat
        last_six_months = (
            (monthly_income - flat_disregard) * p.percentage * remaining_months
        )
        first_six_month = where(
            fully_disregard_eligible, fully_disregard, last_six_months
        )
        total_adjusted_income = first_six_month + last_six_months
        dependent_care_deduction = person(
            "ma_tafdc_dependent_care_deduction", period
        )
        # The income of grandparents is computed separately
        is_grandparent = person("is_grandparent_of_filer_or_spouse", period)
        return (
            max_(0, total_adjusted_income - dependent_care_deduction)
            * ~is_grandparent
        )
