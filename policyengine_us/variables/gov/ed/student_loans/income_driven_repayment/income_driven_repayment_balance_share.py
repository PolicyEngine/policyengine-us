from policyengine_us.model_api import *


class income_driven_repayment_balance_share(Variable):
    value_type = float
    entity = Person
    label = "Income-driven repayment share of the couple's eligible balance"
    documentation = (
        "The person's share of the eligible federal student loan balance held "
        "by the head and spouse of their tax unit. Joint filers whose spouse "
        "also has eligible loans owe this share of the income-driven payment. "
        "Married people filing separately are in separate tax units, so their "
        "share is 1."
    )
    unit = "/1"
    definition_period = YEAR
    reference = (
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(e)(2)(i)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(g)(1)(i)",
    )

    def formula(person, period, parameters):
        balance = person("federal_student_loan_balance", period)
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        eligible_balance = where(is_head_or_spouse, balance, 0)
        couple_balance = person.tax_unit.sum(eligible_balance)
        return np.divide(
            eligible_balance,
            couple_balance,
            out=np.zeros_like(eligible_balance),
            where=couple_balance > 0,
        )
