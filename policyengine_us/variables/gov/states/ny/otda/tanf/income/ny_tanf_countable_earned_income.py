from policyengine_us.model_api import *


class ny_tanf_countable_earned_income(Variable):
    value_type = float
    entity = Person
    label = "New York TANF countable earned income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.NY
    reference = (
        "https://otda.ny.gov/policy/directives/1997/ADM/97_ADM-23.pdf#page=3",
        "https://otda.ny.gov/policy/directives/2022/ADM/22-ADM-11.pdf#page=2",
    )

    def formula(person, period, parameters):
        gross_earned = person("tanf_gross_earned_income", period)
        p = parameters(period).gov.states.ny.otda.tanf
        flat = p.income.earned_income_deduction.flat
        rate = p.income.earned_income_deduction.percent

        if p.reform_2022.in_effect:
            # Post-October 2022: EID first, then work expense
            after_eid = gross_earned * (1 - rate)
            return max_(after_eid - flat, 0)

        # Pre-October 2022: Work expense first, then EID
        after_work_expense = max_(gross_earned - flat, 0)
        return after_work_expense * (1 - rate)
