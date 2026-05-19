from policyengine_us.model_api import *


class ok_tanf_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Oklahoma TANF countable earned income"
    unit = USD
    definition_period = MONTH
    reference = "https://oklahoma.gov/okdhs/library/policy/current/oac-340/chapter-10/subchapter-3/parts-3/earned-income-disregard.html"
    defined_for = StateCode.OK

    def formula(spm_unit, period, parameters):
        # NOTE: OAC 340:10-3-31.1 also provides a 3-month EID period where
        # 100% of earned income is excluded. This applies once per rolling
        # 12-month period when a recipient obtains employment. This 100%
        # disregard is not currently implemented.

        p = parameters(period).gov.states.ok.dhs.tanf.income

        # Sum person-level earned income after work expense
        # Per OAC 340:10-3-33(a): $120 for <30 hrs/week, $240 for 30+ hrs/week
        after_work_expense = add(
            spm_unit,
            period,
            ["ok_tanf_earned_income_after_work_expense_person"],
        )

        # Apply 50% EID if eligible (gross earned <= $2,064)
        eid_eligible = spm_unit("ok_tanf_eid_eligible", period)
        disregard_amount = where(
            eid_eligible,
            after_work_expense * p.disregard.rate,
            0,
        )
        return max_(after_work_expense - disregard_amount, 0)
