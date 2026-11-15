from policyengine_us.model_api import *


class ok_liheap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Oklahoma LIHEAP income eligible"
    defined_for = StateCode.OK
    # OAC 340:20-1-10(h)(2), 340:20-1-11(a): gross income including deemed
    # contributions at or below the Appendix C-7 standard, which winter
    # heating and summer cooling share (plan items 2.1 and 3.1).
    reference = (
        "https://prod-ok-administrativerules.tecuity.com/api/BlobStorageGetFile?storageContainer=TitleHtml&name=Title_340.html",
        "https://oklahoma.gov/content/dam/ok/en/okdhs/documents/searchcenter/okdhsformresults/c-7.pdf",
        # PDF pages 9, 11
        "https://liheapch.acf.gov/docs/2026/state-plans/OK_Plan_2026.pdf#page=9",
    )

    def formula(spm_unit, period, parameters):
        # OAC 340:20-1-11(a) converts income to a monthly amount and rounds it
        # to the nearest dollar; Appendix C-7 prints whole-dollar monthly
        # limits. Rounding the monthly total half up approximates the
        # per-source rounding.
        income = spm_unit("ok_liheap_gross_income", period)
        monthly_income = np.floor(income / MONTHS_IN_YEAR + 0.5)
        monthly_limit = spm_unit("ok_liheap_income_limit", period) / MONTHS_IN_YEAR
        return monthly_income <= monthly_limit
