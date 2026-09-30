from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class nc_lieap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "North Carolina LIEAP regular heating assistance"
    documentation = (
        "Verified for FY2026. Earlier years use model parameter backfilling "
        "and are unverified historical estimates."
    )
    defined_for = "nc_lieap_eligible"
    reference = "https://policies.ncdhhs.gov/wp-content/uploads/EP-300-5.1.2026.pdf#page=18,19,20"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nc.ncdhhs.lieap.payment
        size = spm_unit("nc_lieap_household_size", period)
        income = spm_unit("nc_lieap_income", period) / MONTHS_IN_YEAR
        limit = spm_unit("nc_lieap_income_limit", period) / MONTHS_IN_YEAR
        lower_limit = np.floor(limit * p.lower_income_share + 0.5)
        amount = where(
            income <= lower_limit, p.lower_income.calc(size), p.higher_income.calc(size)
        )
        fuel = spm_unit("heating_type", period)
        types = fuel.possible_values
        solid_fuel = (fuel == types.COAL) | (fuel == types.WOOD)
        # Section 300.12 expressly keeps coal/wood at the regular 130% limit even
        # for a special-population household. Derive that limit using the same FPG.
        policy = parameters(period).gov.states.nc.ncdhhs.lieap
        state_group = spm_unit.household("state_group_str", period)
        guideline = fpg(
            max_(size, 1), state_group, period, parameters, year_lag=policy.fpg_year_lag
        )
        solid_limit = np.floor(guideline * policy.income_limit / MONTHS_IN_YEAR + 0.5)
        solid_amount = where(income <= solid_limit, p.coal_wood, 0)
        # A subsidy can leave an account credit; no current-bill cap is imposed.
        # NONE/UNSPECIFIED do not establish a heating arrangement.
        return where(
            (fuel == types.NONE) | (fuel == types.UNSPECIFIED),
            0,
            where(solid_fuel, solid_amount, amount),
        )
