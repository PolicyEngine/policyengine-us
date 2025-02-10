from policyengine_us.model_api import *


class ma_tafdc_dependent_care_deduction(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) dependent care deduction"
    definition_period = MONTH
    reference = "https://www.masslegalservices.org/content/73-how-much-income-can-you-have-and-still-qualify-tafdc"
    defined_for = StateCode.MA

    def formula(person, period, parameters):
        dependent = person("is_tax_unit_dependent", period)
        total_weekly_hours = (
            person.tax_unit.sum(person("weekly_hours_worked", period))
            * MONTHS_IN_YEAR
        )
        age = person("monthly_age", period)
        p = parameters(
            period
        ).gov.states.ma.dta.tafdc.gross_income.deductions.dependent_care_expenses
        young_child = age < p.young_child_age_threshold
        amount = where(
            young_child,
            p.amount.younger.calc(total_weekly_hours),
            p.amount.older.calc(total_weekly_hours),
        )
        total_amount = amount * dependent
        care_expenses = person("care_expenses", period)
        return min_(total_amount, care_expenses)
