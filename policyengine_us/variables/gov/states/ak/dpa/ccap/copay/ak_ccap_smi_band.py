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
        # Uses the FICS-published AK monthly 100% SMI by family size so the
        # copay band aligns with the same SMI scale that
        # `ak_ccap_smi_threshold` uses for eligibility.
        p = parameters(period).gov.states.ak.dpa.ccap.income
        countable = spm_unit("ak_ccap_countable_income", period)
        size = spm_unit("spm_unit_size", period.this_year)
        monthly_smi = p.smi.amount.calc(size)
        return where(monthly_smi > 0, countable / monthly_smi, 0)
