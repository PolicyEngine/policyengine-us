from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class ak_hap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Alaska HAP federal LIHEAP income limit"
    reference = (
        "http://dpaweb.hss.state.ak.us/manuals/HAP/3000/3000_introductions_and_definitions.htm",
        "http://dpaweb.hss.state.ak.us/manuals/HAP/addendum/addendum_e.htm",
    )
    defined_for = StateCode.AK

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ak.dpa.hap
        size = spm_unit("ak_hap_household_size", period)
        state_group = spm_unit.household("state_group_str", period)
        guideline = fpg(size, state_group, period, parameters, year_lag=p.fpg_year_lag)
        # Numerical reconciliation of all 18 FY2027 published 150% ceilings:
        # floor the monthly FPG, apply the rate, then floor the monthly limit.
        # The source requires downward rounding but does not state this order.
        monthly_limit = np.floor(np.floor(guideline / MONTHS_IN_YEAR) * p.fpg_rate)
        # Return the annual equivalent of the published monthly ceiling.
        # Beyond published sizes, retain the federal additional-person rule;
        # state rounding there and backfilled historical years are unverified.
        return where(size > 0, monthly_limit * MONTHS_IN_YEAR, 0)
