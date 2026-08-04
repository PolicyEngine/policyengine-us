from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import smi


class wa_wccc_smi_fraction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Washington WCCC household income as a fraction of State Median Income"
    definition_period = MONTH
    defined_for = StateCode.WA
    reference = "https://app.leg.wa.gov/wac/default.aspx?cite=110-15-0075"

    def formula(spm_unit, period, parameters):
        year = period.start.year
        month = period.start.month
        if month >= 10:
            instant_str = f"{year}-10-01"
        else:
            instant_str = f"{year - 1}-10-01"
        size = spm_unit("spm_unit_size", period.this_year)
        state = spm_unit.household("state_code_str", period.this_year)
        monthly_smi = smi(size, state, instant_str, parameters) / MONTHS_IN_YEAR
        countable_income = spm_unit("wa_wccc_countable_income", period)
        return where(monthly_smi > 0, countable_income / monthly_smi, 0)
