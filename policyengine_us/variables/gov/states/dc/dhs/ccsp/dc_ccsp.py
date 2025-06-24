from policyengine_us.model_api import *


class dc_ccsp(Variable):
    value_type = float
    entity = SPMUnit
    label = "DC Child Care Subsidy Program (CCSP) benefit amount"
    definition_period = MONTH
    reference = "https://osse.dc.gov/subsidy"
    defined_for = "dc_ccsp_eligible"

    def formula(spm_unit, period, parameters):
        co_payment = spm_unit("dc_ccsp_co_payment", period)
        child_care_expense = spm_unit(
            "spm_unit_pre_subsidy_childcare_expenses", period
        )
        return max_(child_care_expense - co_payment, 0)
