from policyengine_us.model_api import *


class ut_heat_energy_cost_standard(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Utah HEAT annual energy cost standard"
    defined_for = StateCode.UT
    reference = "https://jobs.utah.gov/infosource/heatpolicy/Policy/600_Payment_Calculation/609_Table_III_Monthly_Energy_Cost_Standards.htm"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ut.dwf.heat.benefit
        dwelling = spm_unit("ut_heat_dwelling_type", period)
        standard = p.monthly_energy_cost_standard[dwelling]
        fuel = spm_unit("heating_type", period)
        fuels = fuel.possible_values
        monthly_standard = select(
            [
                fuel == fuels.NATURAL_GAS,
                (fuel == fuels.PROPANE) | (fuel == fuels.KEROSENE),
                fuel == fuels.FUEL_OIL,
                fuel == fuels.ELECTRICITY,
                (fuel == fuels.COAL) | (fuel == fuels.OTHER),
                fuel == fuels.WOOD,
            ],
            [
                standard.natural_gas,
                standard.propane,
                standard.fuel_oil,
                standard.electricity,
                standard.coal,
                standard.wood,
            ],
            # UNSPECIFIED and SOLAR have no verified schedule; zero denotes
            # unsupported model coverage, not a legal zero-cost standard.
            # NONE means no home heating and never qualifies.
            default=0,
        )
        return monthly_standard * MONTHS_IN_YEAR
