from policyengine_us.model_api import *


class ak_ccap_smi_band(Variable):
    value_type = float
    entity = SPMUnit
    label = "Alaska CCAP countable income as share of State Median Income"
    definition_period = MONTH
    unit = "/1"
    defined_for = StateCode.AK
    reference = "https://health.alaska.gov/media/okdlx2xm/alaska-fics.pdf#page=1"

    def formula(spm_unit, period, parameters):
        # Uses the federal hhs_smi (which equals the Alaska FICS table
        # for AK at every family size) so the copay band aligns with the
        # same SMI scale that `ak_ccap_smi_threshold` uses for eligibility.
        countable = spm_unit("ak_ccap_countable_income", period)
        annual_smi = spm_unit("hhs_smi", period.this_year)
        monthly_smi = annual_smi / MONTHS_IN_YEAR
        return where(monthly_smi > 0, countable / monthly_smi, 0)
