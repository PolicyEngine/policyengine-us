from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class ak_hap_income_factor(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "Alaska HAP income factor"
    reference = (
        "http://dpaweb.hss.state.ak.us/manuals/HAP/3004/3004-5_grant_computation.htm",
        "http://dpaweb.hss.state.ak.us/manuals/HAP/addendum/addendum_e.htm",
    )
    defined_for = StateCode.AK

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ak.dpa.hap
        size = spm_unit("ak_hap_household_size", period)
        income = spm_unit("ak_hap_countable_income", period)
        state_group = spm_unit.household("state_group_str", period)
        guideline = fpg(size, state_group, period, parameters, year_lag=p.fpg_year_lag)
        monthly_fpg = np.floor(guideline / MONTHS_IN_YEAR)
        # Reconcile the published grid by flooring the monthly FPG before each
        # percentage. This gives 415, not the printed 407, at the FY2027 size-1
        # 25% ceiling. 407 matches the prior-year base; using 415 follows the
        # explicit 25% rule, not an agency-issued correction. Historical years
        # are unverified backfilled estimates.
        limits = [
            np.floor(monthly_fpg * rate) * MONTHS_IN_YEAR
            for rate in p.income_factor.fpg_rates
        ]
        factor = select(
            [income <= limit for limit in limits], p.income_factor.factors, default=0
        )
        return where(size > 0, factor, 0)
