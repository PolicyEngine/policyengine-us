from policyengine_us.model_api import *


class ny_ccap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Income eligible for the New York Child Care Assistance Program"
    defined_for = StateCode.NY
    documentation = (
        "Social Services Law 410-w caps eligibility at 85 percent of the "
        "state median income, the sole ceiling since the October 1, 2023 "
        "statutory revisions replaced the state income standard limit. OCFS "
        "publishes its state median income figures for a June 1 to May 31 "
        "year, while hhs_smi is keyed to the federal October 1 series and "
        "resolved annually, so the ceiling here lags New York's own table "
        "for the June to December months of each year."
    )
    reference = (
        "https://www.nysenate.gov/legislation/laws/SOS/410-W",
        "https://dos.ny.gov/system/files/documents/2024/05/050124.pdf#page=12",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ny.ocfs.ccap.income
        income = spm_unit("ny_ccap_countable_income", period)
        # Social Services Law 410-w caps eligibility at 85 percent of the
        # state median income, the sole ceiling since the October 1, 2023
        # statutory revisions replaced the state income standard limit.
        smi_limit = spm_unit("hhs_smi", period) * p.income_limit_smi_rate
        return income <= smi_limit
