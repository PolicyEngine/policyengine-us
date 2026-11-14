from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class id_iccp_fpg(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    definition_period = MONTH
    label = "Idaho Child Care Program monthly federal poverty guideline"
    defined_for = StateCode.ID
    reference = "https://healthandwelfare.idaho.gov/services-programs/children-families/apply-child-care"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.id.dhw.iccp.income
        size = spm_unit("spm_unit_size", period.this_year)
        state_group = spm_unit.household("state_group_str", period.this_year)
        annual_fpg = fpg(size, state_group, period, parameters, year_lag=p.fpg_year_lag)
        return annual_fpg / MONTHS_IN_YEAR
