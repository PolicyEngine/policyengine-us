from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class ak_hap_income_factor(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "Alaska HAP income factor"
    reference = (
        "https://www.akleg.gov/basis/aac.asp?media=print&secStart=7.44.010&secEnd=7.44.9001",
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
        # 7 AAC 44.040(a)(4) and 44.080(i) compare gross monthly income with
        # exact percentages of the monthly Alaska poverty guideline; annual
        # amounts compare the same way. Historical years are unverified
        # backfilled estimates.
        limits = [guideline * rate for rate in p.income_factor.fpg_rates]
        factor = select(
            [income <= limit for limit in limits], p.income_factor.factors, default=0
        )
        return where(size > 0, factor, 0)
