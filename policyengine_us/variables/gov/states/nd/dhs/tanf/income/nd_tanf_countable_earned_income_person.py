from policyengine_us.model_api import *


class nd_tanf_countable_earned_income_person(Variable):
    value_type = float
    entity = Person
    label = "North Dakota TANF countable earned income per person"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.nd.gov/dhs/policymanuals/40019/400_19_105_25.htm",
        "https://www.law.cornell.edu/regulations/north-dakota/N-D-A-C-75-02-1.2-51",
    )
    defined_for = StateCode.ND

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nd.dhs.tanf.income.deductions
        gross_earned = person("tanf_gross_earned_income", period)

        # Standard Employment Expense: max(27%, $180) per person with earnings
        has_earnings = gross_earned > 0
        percentage_amount = gross_earned * p.standard_employment_expense.rate
        standard_expense = where(
            has_earnings,
            max_(percentage_amount, p.standard_employment_expense.minimum),
            0,
        )

        # Time Limited Percentage (TLP): declining rate based on calendar month proxy
        # Uses calendar month (1-12) as proxy for participation months.
        # In reality, TLP tracks cumulative participation months and ends after 12.
        # Months 1-6: 50%, Months 7-9: 35%, Months 10-12: 25%
        earned_after_expense = max_(gross_earned - standard_expense, 0)
        month = period.start.month
        tlp_rate = p.time_limited_percentage.rate.calc(month)
        tlp_deduction = earned_after_expense * tlp_rate

        return max_(earned_after_expense - tlp_deduction, 0)
