from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import smi


class ak_ccap_smi_band(Variable):
    value_type = float
    entity = SPMUnit
    label = "Alaska CCAP countable income as share of State Median Income"
    definition_period = MONTH
    unit = "/1"
    defined_for = StateCode.AK
    reference = "https://health.alaska.gov/media/okdlx2xm/alaska-fics.pdf#page=1"

    def formula(spm_unit, period, parameters):
        countable = spm_unit("ak_ccap_countable_income", period)
        size = spm_unit("spm_unit_size", period.this_year)
        state = spm_unit.household("state_code_str", period.this_year)
        annual_smi = smi(size, state, period.this_year, parameters)
        monthly_smi = annual_smi / MONTHS_IN_YEAR
        return where(monthly_smi > 0, countable / monthly_smi, 0)
