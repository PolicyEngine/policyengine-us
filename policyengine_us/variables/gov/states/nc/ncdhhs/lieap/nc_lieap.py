from policyengine_us.model_api import *


class nc_lieap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "North Carolina LIEAP regular heating assistance"
    documentation = (
        "Verified for FY2026 and FY2027. The year is the heating season ending "
        "in that year, so 2026 is federal fiscal year 2026, with applications "
        "from December 2025 through March 2026. Earlier years use model "
        "parameter backfilling and are unverified historical estimates. The "
        "manual publishes income limits for 1 to 26 eligible members and "
        "payment bands for 1 to 15 members (130% limit) or 1 to 11 members "
        "(150% limit); for larger households the limits and bands are "
        "extrapolated with the same poverty guideline formula."
    )
    defined_for = "nc_lieap_eligible"
    reference = (
        # Section 300.09 (page 10), Section 300.12 A (page 18) and the Section
        # 300.12 B payment charts (pages 19-20).
        "https://policies.ncdhhs.gov/wp-content/uploads/EP-300-5.1.2026.pdf#page=18",
    )

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
        # NONE means the home has no heat. UNSPECIFIED is paid only when heat is
        # included in rent: EP-300.08 item 4 makes that public housing household
        # fully vulnerable, and the payment does not depend on its fuel.
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        no_schedule = (fuel == types.NONE) | (
            (fuel == types.UNSPECIFIED) & ~heat_in_rent
        )
        return where(no_schedule, 0, where(solid_fuel, p.coal_wood, amount))
