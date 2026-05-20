from policyengine_us.model_api import *


class sc_ccap(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "South Carolina CCAP benefit amount"
    definition_period = MONTH
    defined_for = "sc_ccap_eligible"
    reference = (
        "https://www.scchildcare.org/media/ubhdm1at/1-13-2025_policy-manual.pdf#page=183",
        "https://www.scchildcare.org/media/cr5dc51w/submitted-version-of-the-ccdf-ffy-2025-2027-for-south-carolina-as-of-7-1-24pdf.pdf#page=17",
    )

    def formula(spm_unit, period, parameters):
        copay = spm_unit("sc_ccap_copay", period)
        maximum_weekly_benefit = add(
            spm_unit, period, ["sc_ccap_maximum_weekly_benefit"]
        )
        maximum_monthly_benefit = maximum_weekly_benefit * (
            WEEKS_IN_YEAR / MONTHS_IN_YEAR
        )
        pre_subsidy_childcare_expenses = spm_unit(
            "spm_unit_pre_subsidy_childcare_expenses", period
        )
        uncapped = max_(pre_subsidy_childcare_expenses - copay, 0)
        return min_(uncapped, maximum_monthly_benefit)
