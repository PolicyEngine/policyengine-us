from policyengine_us.model_api import *


class ok_liheap_cooling(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Oklahoma LIHEAP regular summer cooling assistance"
    defined_for = "ok_liheap_cooling_eligible"
    # OAC 340:20-1-10(i)(2): "summer cooling is based on household size and
    # net income"; 340:20-1-20(d) refers to Appendix C-7-A for the amounts.
    reference = (
        "https://prod-ok-administrativerules.tecuity.com/api/BlobStorageGetFile?storageContainer=TitleHtml&name=Title_340.html",
        "https://oklahoma.gov/content/dam/ok/en/okdhs/documents/searchcenter/okdhsformresults/c-7-a.pdf#page=2",
        # PDF pages 4, 12
        "https://liheapch.acf.gov/docs/2026/state-plans/OK_Plan_2026.pdf#page=4",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ok.dhs.liheap.cooling
        size = spm_unit("ok_liheap_household_size", period)
        # OAC 340:20-1-11(a) rounds monthly income to the nearest dollar, and
        # Appendix C-7-A prints whole-dollar bands, so round half up first.
        net_income = spm_unit("ok_liheap_net_income", period)
        monthly_income = np.floor(net_income / MONTHS_IN_YEAR + 0.5)
        band = p.income_band.calc(monthly_income).astype(int)
        size_group = p.household_size_group.calc(size).astype(int)
        # One payment per household each year, the same for every cooling
        # energy source and dwelling, with no bill cap. The equipment
        # reimbursement, which replaces the bill payment, is not modeled.
        return p.amount[band][size_group]
