from policyengine_us.model_api import *


class ut_heat_energy_cost_standard(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Utah HEAT annual energy cost standard"
    defined_for = StateCode.UT
    reference = (
        "https://jobs.utah.gov/infosource/heatpolicy/Policy/600_Payment_Calculation/609_Table_III_Monthly_Energy_Cost_Standards.htm",
        "https://jobs.utah.gov/infosource/heatpolicy/Policy/600_Payment_Calculation/603_Energy_Burden.htm",
        "https://jobs.utah.gov/infosource/heatpolicy/Policy/Obsolete_Policy/Obsolete_200/Obsolete_207_(01_01_25_to_09_30_26)_Eligible_Households-copy.htm",
        "https://liheapch.acf.gov/docs/2026/state-plans/UT_Plan_2026.pdf#page=4",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ut.dwf.heat.benefit
        dwelling = spm_unit("ut_heat_dwelling_type", period)
        standard = p.monthly_energy_cost_standard[dwelling]
        fuel = spm_unit("heating_type", period)
        fuels = fuel.possible_values
        # HEAT is one benefit a program year covering heating and cooling
        # (plan item 1.1, section 207), and section 603 takes the standard for
        # the household's primary energy source. A home with no heating that
        # pays an electric bill therefore uses the electricity standard. Solar
        # homes are taken as grid-tied with electric supplemental heat, as
        # heating_expense reads their electricity bill.
        electric_without_heating = (fuel == fuels.NONE) & (
            spm_unit("pre_subsidy_electricity_expense", period) > 0
        )
        monthly_standard = select(
            [
                fuel == fuels.NATURAL_GAS,
                (fuel == fuels.PROPANE) | (fuel == fuels.KEROSENE),
                fuel == fuels.FUEL_OIL,
                (fuel == fuels.ELECTRICITY)
                | (fuel == fuels.SOLAR)
                | electric_without_heating,
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
            # UNSPECIFIED has no verified schedule; zero denotes unsupported
            # model coverage, not a legal zero-cost standard. A NONE household
            # with no electric bill is not connected to an energy source
            # (section 208) and never qualifies.
            default=0,
        )
        return monthly_standard * MONTHS_IN_YEAR
