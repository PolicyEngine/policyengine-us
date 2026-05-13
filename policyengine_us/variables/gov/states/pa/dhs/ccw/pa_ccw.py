from policyengine_us.model_api import *


class pa_ccw(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Pennsylvania Child Care Works benefit amount"
    definition_period = MONTH
    defined_for = "pa_ccw_eligible"
    reference = (
        "https://www.pacodeandbulletin.gov/secure/pacode/data/055/chapter3042/055_3042.pdf#page=10",
        "https://www.pacodeandbulletin.gov/secure/pacode/data/055/chapter3042/055_3042.pdf#page=32",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.pa.dhs.ccw
        copay = spm_unit("pa_ccw_copay", period)
        maximum_monthly_payment = add(
            spm_unit, period, ["pa_ccw_maximum_monthly_payment"]
        )
        pre_subsidy_childcare_expenses = spm_unit(
            "spm_unit_pre_subsidy_childcare_expenses", period
        )
        uncapped = max_(pre_subsidy_childcare_expenses - copay, 0)
        benefit = min_(uncapped, maximum_monthly_payment)
        min_monthly_payment = p.min_dept_payment * WEEKS_IN_YEAR / MONTHS_IN_YEAR
        return where(benefit >= min_monthly_payment, benefit, 0)
