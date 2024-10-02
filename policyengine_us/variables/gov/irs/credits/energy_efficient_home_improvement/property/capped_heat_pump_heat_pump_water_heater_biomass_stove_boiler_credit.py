from policyengine_us.model_api import *


class capped_heat_pump_heat_pump_water_heater_biomass_stove_boiler_credit(
    Variable
):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Capped credit on heat pumps, heat pump water heaters, and biomass stoves and boilers"
    documentation = "Capped credit on heat pumps, heat pump water heaters, and biomass stoves and boilers"
    unit = USD
    reference = "https://www.democrats.senate.gov/imo/media/doc/inflation_reduction_act_of_2022.pdf#page=340"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.irs.credits.energy_efficient_home_improvement
        pre_rebate_expenditure = add(
            tax_unit,
            period,
            [
                i + "_expenditures"
                for i in p.qualified_expenditures.heat_pump_heat_pump_water_heater_biomass_stove_boiler
            ],
        )
        # NB: We assume that the credit is based on after-rebate expenditures,
        # where rebates are per-item before the total rebate cap is applied.
        REBATE_ELEMENTS = ["heat_pump", "heat_pump_water_heater"]
        rebates = add(
            tax_unit,
            period,
            ["capped_" + i + "_rebate" for i in REBATE_ELEMENTS],
        )
        post_rebate_expenditure = pre_rebate_expenditure - rebates
        rate = p.rates.property
        uncapped = post_rebate_expenditure * rate
        # Cap at either the total property cap (pre-IRA) or heat pump etc. cap (post-IRA).
        # We represent pre-IRA as an infinite heat pump cap.
        heat_pump_etc_cap = (
            p.cap.annual.heat_pump_heat_pump_water_heater_biomass_stove_boiler
        )
        if heat_pump_etc_cap == np.inf:
            cap = p.cap.annual.energy_efficient_building_property
        else:
            cap = heat_pump_etc_cap
        return min_(uncapped, cap)
