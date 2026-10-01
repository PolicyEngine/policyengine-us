from policyengine_us.model_api import *


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
    reference = "https://policies.ncdhhs.gov/wp-content/uploads/EP-300-5.1.2026.pdf#page=10,18,19,20"

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
        # Every income-eligible coal or wood household receives the flat amount
        # (EP-300 pages 10, 18 and 20). Section 300.12 A names 130% as the income
        # limit for all households, so its coal/wood sentence is read as restating
        # income eligibility; Section 300.09 sets that limit at 150% for the
        # special population, which therefore qualifies up to its own limit.
        # A subsidy can leave an account credit; no current-bill cap is imposed.
        # NONE/UNSPECIFIED do not establish a heating arrangement.
        return where(
            (fuel == types.NONE) | (fuel == types.UNSPECIFIED),
            0,
            where(solid_fuel, p.coal_wood, amount),
        )
