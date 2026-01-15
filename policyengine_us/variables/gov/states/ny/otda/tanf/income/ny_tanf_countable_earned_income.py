from policyengine_us.model_api import *


class ny_tanf_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "New York TANF countable earned income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.NY
    reference = (
        "https://otda.ny.gov/policy/directives/1997/ADM/97_ADM-23.pdf",
        "https://otda.ny.gov/policy/directives/2022/ADM/22-ADM-11.pdf#page=2",
    )

    def formula(spm_unit, period, parameters):
        gross_earned = spm_unit("ny_tanf_gross_earned_income", period)
        p = parameters(period).gov.states.ny.otda.tanf

        eid_rate = p.income.earned_income_deduction.percent
        work_expense = p.income.earned_income_deduction.flat

        if p.reform_2022.in_effect:
            # Post-October 2022: EID first, then work expense
            # https://otda.ny.gov/policy/gis/2022/22DC085.pdf Section 2
            return max_(gross_earned * (1 - eid_rate) - work_expense, 0)

        # Pre-October 2022: Work expense first, then EID
        # https://otda.ny.gov/policy/directives/1997/ADM/97_ADM-23.pdf
        after_work_expense = max_(gross_earned - work_expense, 0)
        return after_work_expense * (1 - eid_rate)
