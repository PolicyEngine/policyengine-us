from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import smi


class ak_ccap_smi_threshold(Variable):
    value_type = float
    entity = SPMUnit
    label = "Alaska CCAP monthly State Median Income eligibility threshold"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.AK
    reference = (
        "https://www.akleg.gov/basis/aac.asp",
        "https://health.alaska.gov/media/okdlx2xm/alaska-fics.pdf#page=1",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ak.dpa.ccap.income
        size = spm_unit("spm_unit_size", period.this_year)
        state = spm_unit.household("state_code_str", period.this_year)
        annual_smi = smi(size, state, period.this_year, parameters)
        return annual_smi * p.smi_rate / MONTHS_IN_YEAR
