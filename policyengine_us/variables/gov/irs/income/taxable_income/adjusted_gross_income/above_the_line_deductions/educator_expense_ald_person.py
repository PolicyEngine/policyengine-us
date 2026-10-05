from policyengine_us.model_api import *


class educator_expense_ald_person(Variable):
    value_type = float
    entity = Person
    label = "Educator expense deduction for each person"
    unit = USD
    documentation = (
        "Each person's educator expenses, capped at the per-educator limit of "
        "26 USC 62(a)(2)(D). This is the amount for the person's own return; "
        "educator_expense_ald adds the head's and spouse's amounts for the "
        "tax unit's return."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/62#a_2_D",
        "https://www.law.cornell.edu/uscode/text/26/62#d",
    )

    def formula(person, period, parameters):
        expenses = max_(0, person("educator_expense", period))
        cap = parameters(period).gov.irs.ald.educator_expense.cap
        return min_(expenses, cap)
