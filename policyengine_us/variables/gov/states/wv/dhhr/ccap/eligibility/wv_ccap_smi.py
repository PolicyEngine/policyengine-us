from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import smi


class wv_ccap_smi(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    definition_period = MONTH
    label = "West Virginia CCAP monthly state median income"
    defined_for = StateCode.WV
    reference = (
        # PDF pages 5-6
        "https://bfa.wv.gov/media/6826/download?inline#page=5",
    )

    def formula(spm_unit, period, parameters):
        # Each federal state median income table starts on October 1. Select the
        # table for the program year, shifted back by smi_year_lag while Appendix A
        # keeps the October 2024 table.
        p = parameters(period).gov.states.wv.dhhr.ccap.income
        year = period.start.year
        program_year = year if period.start.month >= 10 else year - 1
        table_year = program_year - int(p.smi_year_lag)
        size = spm_unit("spm_unit_size", period.this_year)
        state = spm_unit.household("state_code_str", period.this_year)
        annual_smi = smi(size, state, f"{table_year}-10-01", parameters)
        return annual_smi / MONTHS_IN_YEAR
