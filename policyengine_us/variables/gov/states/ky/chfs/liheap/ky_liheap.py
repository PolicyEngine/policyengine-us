from policyengine_us.model_api import *


class ky_liheap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Kentucky LIHEAP regular heating assistance"
    defined_for = "ky_liheap_eligible"
    reference = "https://liheapch.acf.gov/docs/2026/benefits-matricies/KY_BenefitMatrix_Heat-Cool_2026.xlsx"

    def formula_2026(spm_unit, period, parameters):
        p = parameters(period).gov.states.ky.chfs.liheap.payment
        income = spm_unit("ky_liheap_income", period) / MONTHS_IN_YEAR
        fpg = spm_unit("ky_liheap_fpg", period) / MONTHS_IN_YEAR
        size = spm_unit("spm_unit_size", period)
        fuel = spm_unit("heating_type", period)
        types = fuel.possible_values
        subsidized = (
            spm_unit("receives_housing_assistance", period)
            | spm_unit.household("is_in_public_housing", period)
            | (spm_unit.household("hud_utility_allowance", period) > 0)
        )
        band = 0
        for rate in p.income_bands:
            band = band + (income > np.ceil(fpg * rate))
        income_points = where(
            subsidized,
            p.income_points.subsidized.calc(band),
            p.income_points.unsubsidized.calc(band),
        )
        fuel_points = p.fuel_points[fuel]
        coal_adjustment = (fuel == types.COAL) * p.coal_adjustment.calc(size)
        points = (
            min_(size, p.maximum_household_points)
            + income_points
            + fuel_points
            + coal_adjustment
        )
        # Reproduces every heating cell in "rev benefit income range", including
        # its reversed subsidized income points and two-person coal exception.
        # That sheet uses 2025 FPG despite its stale title and matches the FY2026
        # plan's $15-$250 range. The conditional "if no funding FFY26" sheet is
        # not used. These source inconsistencies need agency clarification.
        amount = np.ceil(points * p.dollars_per_point)
        amount = where(subsidized, np.ceil(amount * p.subsidized_housing_rate), amount)
        # No verified table mapping exists for OTHER/SOLAR/UNSPECIFIED/NONE.
        # The full seasonal subsidy may credit the account, so it is not capped
        # at the current bill. Coverage starts in 2026, not program inception.
        return where(fuel_points > 0, amount, 0)
