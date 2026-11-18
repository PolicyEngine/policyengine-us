from policyengine_us.model_api import *


class acp(Variable):
    value_type = float
    entity = SPMUnit
    label = "Affordable Connectivity Program"
    documentation = "Affordable Connectivity Program amount"
    definition_period = YEAR
    unit = USD
    defined_for = "is_acp_eligible"
    reference = (
        "https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title47-section1752&edition=prelim",
        "https://www.govinfo.gov/content/pkg/USCODE-2021-title47/html/USCODE-2021-title47-chap16.htm",
        "https://docs.fcc.gov/public/attachments/DA-21-1654A1.pdf#page=3",
        "https://docs.fcc.gov/public/attachments/FCC-22-2A1.pdf#page=5",
        "https://docs.fcc.gov/public/attachments/DA-24-195A1.pdf#page=1",
        "https://docs.fcc.gov/public/attachments/DA-24-342A1.pdf#page=1",
    )

    def formula(spm_unit, period, parameters):
        # Allocate the annual cost uniformly; this does not reconstruct bills.
        monthly_cost = (
            max_(spm_unit("broadband_cost_after_lifeline", period), 0) / MONTHS_IN_YEAR
        )
        tribal = spm_unit.household("is_on_tribal_land", period)
        annual_ebb_positive = spm_unit("ebb", period) > 0
        total = 0
        for month in period.get_subperiods(MONTH):
            fcc = parameters(month.stop).gov.fcc
            acp_cap = where(tribal, fcc.acp.amount.tribal, fcc.acp.amount.standard)
            ebb_cap = where(tribal, fcc.ebb.amount.tribal, fcc.ebb.amount.standard)
            # Use annual EBB as a proxy only in funded EBB months.
            ebb_month = annual_ebb_positive & (ebb_cap > 0)
            total += where(ebb_month, 0, min_(monthly_cost, acp_cap))
        return total
