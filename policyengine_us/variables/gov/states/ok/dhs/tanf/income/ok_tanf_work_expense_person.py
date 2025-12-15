from policyengine_us.model_api import *


class ok_tanf_work_expense_person(Variable):
    value_type = float
    entity = Person
    label = "Oklahoma TANF work expense deduction per person"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/oklahoma/OAC-340-10-3-33"
    )
    defined_for = StateCode.OK

    def formula(person, period, parameters):
        # Per OAC 340:10-3-33(a): Work expense based on weekly hours
        # $120 for <30 hours/week, $240 for 30+ hours/week
        p = parameters(period).gov.states.ok.dhs.tanf.income
        weekly_hours = person("weekly_hours_worked", period.this_year)

        # Only apply work expense if person has earnings
        has_earnings = person("tanf_gross_earned_income", period) > 0

        work_expense = p.deductions.work_expense.calc(weekly_hours)
        return where(has_earnings, work_expense, 0)
