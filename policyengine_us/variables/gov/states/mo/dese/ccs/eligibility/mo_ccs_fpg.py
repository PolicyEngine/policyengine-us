from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class mo_ccs_fpg(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    definition_period = MONTH
    label = "Missouri Child Care Subsidy monthly federal poverty guideline"
    defined_for = StateCode.MO
    reference = "https://dese.mo.gov/sites/g/files/zuston521/files/media/pdf/2026/07/Income%20Elig%20_Updated%206.29.26.pdf#page=1"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.mo.dese.ccs.income
        size = spm_unit("spm_unit_size", period.this_year)
        state_group = spm_unit.household("state_group_str", period.this_year)
        annual_fpg = fpg(size, state_group, period, parameters, year_lag=p.fpg_year_lag)
        return annual_fpg / MONTHS_IN_YEAR
