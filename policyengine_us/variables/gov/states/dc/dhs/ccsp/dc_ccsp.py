from policyengine_us.model_api import *


class dc_ccsp(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "DC Child Care Subsidy Program (CCSP) benefit amount"
    definition_period = MONTH
    reference = "https://osse.dc.gov/subsidy"
    defined_for = "dc_ccsp_eligible"

    def formula(spm_unit, period, parameters):
        copay = spm_unit("dc_ccsp_copay", period)
        maximum_payment = add(
            spm_unit, period, ["dc_ccsp_maximum_subsidy_amount"]
        )
        pre_subsidy_childcare_expense = spm_unit(
            "spm_unit_pre_subsidy_childcare_expenses", period
        )
        uncapped_subsidy_amount = max_(
            pre_subsidy_childcare_expense - copay, 0
        )
        return min_(uncapped_subsidy_amount, maximum_payment)
