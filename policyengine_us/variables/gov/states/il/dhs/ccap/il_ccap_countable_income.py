from policyengine_us.model_api import *


class il_ccap_countable_income(Variable):
    value_type = float
    unit = USD
    entity = SPMUnit
    label = "Illinois Child Care Assistance Program (CCAP) countable income"
    definition_period = MONTH
    reference = (
        "https://www.dhs.state.il.us/page.aspx?item=10163",
        "https://www.dhs.state.il.us/page.aspx?item=10160",
    )
    defined_for = StateCode.IL

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.il.dhs.ccap.income
        person = spm_unit.members
        gross_income = add(
            spm_unit,
            period,
            p.countable_income.sources,
        )
        child_earnings = (
            person("earned_income", period) + person("farm_operations_income", period)
        ) * person("is_child", period.this_year)
        child_support_paid = add(
            spm_unit,
            period,
            ["child_support_expense"],
        )
        return max_(
            gross_income
            - spm_unit.sum(child_earnings)
            - child_support_paid * p.deductions.child_support_rate,
            0,
        )
