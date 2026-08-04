from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import smi


class wa_wccc_smi_limit(Variable):
    value_type = float
    entity = SPMUnit
    label = "Washington WCCC monthly income limit"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.WA
    reference = "https://app.leg.wa.gov/wac/default.aspx?cite=110-15-0005"

    def formula(spm_unit, period, parameters):
        year = period.start.year
        month = period.start.month
        if month >= 10:
            instant_str = f"{year}-10-01"
        else:
            instant_str = f"{year - 1}-10-01"
        size = spm_unit("spm_unit_size", period.this_year)
        state = spm_unit.household("state_code_str", period.this_year)
        annual_smi = smi(size, state, instant_str, parameters)
        rate = spm_unit("wa_wccc_smi_rate", period)
        return annual_smi * rate / MONTHS_IN_YEAR
