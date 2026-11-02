from policyengine_us.model_api import *


class co_leap_heating_cost(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Colorado LEAP estimated heating cost"
    defined_for = StateCode.CO
    # PDF pages 1-2,6
    reference = "https://liheapch.acf.gov/docs/2026/benefits-matricies/CO_BenefitMatrix_Heat-Crisis_2026.pdf#page=1"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.co.cdhs.leap.payment
        dwelling = spm_unit("co_leap_dwelling_type", period)
        fuel = spm_unit("heating_type", period)
        fuels = fuel.possible_values
        included = spm_unit("heat_expense_included_in_rent", period)
        # Existing annual expense proxies the covered heating-season bill.
        # It cannot identify actual prior November-April history or vendor
        # approval. Explicit zero does not trigger a missing-history flat rate.
        expense = max_(spm_unit("heating_expense", period), 0)
        # No Colorado source lists solar heat. A solar home is treated as
        # electric: heating_expense reads its electric bill, and the rate
        # tables have no solar column, so it takes the electric share and
        # the electric rent standard.
        electric = (fuel == fuels.ELECTRICITY) | (fuel == fuels.SOLAR)
        electric_share = where(electric, p.electric_heat_share[dwelling], 1)
        table = p.heat_in_rent
        included_cost = select(
            [
                fuel == fuels.NATURAL_GAS,
                fuel == fuels.PROPANE,
                electric,
                fuel == fuels.WOOD,
                (fuel == fuels.FUEL_OIL)
                | (fuel == fuels.KEROSENE)
                | (fuel == fuels.COAL),
            ],
            [
                table.natural_gas[dwelling],
                table.propane[dwelling],
                table.electricity[dwelling],
                table.wood[dwelling],
                table.oil_kerosene_coal[dwelling],
            ],
            default=0,
        )
        # Inference: Step G reaches every Step A cost and the Step C table covers
        # total electric costs, so the electric rent standard also takes the
        # share, applied exactly once. Fuel oil reads the rate column headed Fuel
        # Oil/Kerosene (inference); the rate tables also print a column headed
        # Propane Fuel Oil.
        # Propane uses bulk rates and wood purchased rates; bottle/gathered
        # distinctions lack inputs.
        # Unknown rent-included fuels have no supported rate and remain a gap.
        return where(included, included_cost, expense) * electric_share
