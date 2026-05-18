from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import smi


class nj_ccap_smi(Variable):
    value_type = float
    entity = SPMUnit
    label = "New Jersey CCAP 85% State Median Income exit threshold"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.NJ
    reference = (
        "https://www.childcarenj.gov/ChildCareNJ/media/media_library/Income_Eligibility_Schedule.pdf",
        "https://www.childcarenj.gov/ChildCareNJ/media/media_library/CCDF_State_Plan_for_New_Jersey_FFY25-27.pdf#page=34",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nj.njdhs.ccap.income.fpl_rate
        year = period.start.year
        month = period.start.month
        if month >= 10:
            instant_str = f"{year}-10-01"
        else:
            instant_str = f"{year - 1}-10-01"
        size = spm_unit("spm_unit_size", period.this_year)
        state = spm_unit.household("state_code_str", period.this_year)
        annual_smi = smi(size, state, instant_str, parameters)
        return annual_smi * p.smi_exit / MONTHS_IN_YEAR
