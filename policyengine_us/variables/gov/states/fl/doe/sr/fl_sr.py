from policyengine_us.model_api import *


class fl_sr(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Florida School Readiness program benefit"
    definition_period = MONTH
    defined_for = "is_fl_sr_eligible"
    reference = (
        "https://flrules.elaws.us/fac/6m-4.400",
        "https://www.flsenate.gov/laws/statutes/2024/1002.84",
    )

    def formula(spm_unit, period, parameters):
        # spm_unit_pre_subsidy_childcare_expenses is YEAR-defined; the bare
        # monthly period auto-divides the annual amount to a monthly value.
        monthly_expenses = spm_unit("spm_unit_pre_subsidy_childcare_expenses", period)
        copay = spm_unit("fl_sr_copay", period)
        # The statewide provider maximum reimbursement rate (6M-4.500) is set
        # locally by each Early Learning Coalition and is not modeled at the
        # moment, so the subsidy is not capped at a published rate.
        return max_(monthly_expenses - copay, 0)
