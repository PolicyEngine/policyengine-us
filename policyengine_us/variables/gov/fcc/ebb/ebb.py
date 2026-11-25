from policyengine_us.model_api import *


class ebb(Variable):
    value_type = float
    entity = SPMUnit
    label = "Emergency Broadband Benefit amount"
    documentation = "Emergency Broadband Benefit amount"
    definition_period = YEAR
    unit = USD
    defined_for = "is_ebb_eligible"
    reference = (
        "https://www.govinfo.gov/content/pkg/USCODE-2021-title47/html/USCODE-2021-title47-chap16.htm",
        "https://docs.fcc.gov/public/attachments/FCC-22-2A1.pdf#page=3",
        "https://docs.fcc.gov/public/attachments/DA-21-1654A1.pdf#page=4",
    )

    def formula(spm_unit, period, parameters):
        # Allocate the annual cost uniformly; this does not reconstruct bills.
        monthly_cost = (
            max_(spm_unit("broadband_cost_after_lifeline", period), 0) / MONTHS_IN_YEAR
        )
        tribal = spm_unit.household("is_on_tribal_land", period)
        total = 0
        for month in period.get_subperiods(MONTH):
            p = parameters(month.stop).gov.fcc.ebb
            monthly_cap = where(tribal, p.amount.tribal, p.amount.standard)
            total += min_(monthly_cost, monthly_cap)
        return total
