from policyengine_us.model_api import *


class ny_clean_heat_others_incentives(Variable):
    value_type = float
    entity = Household
    label = "NYS Clean Heat Program incentives for electric heat pump installation for CH&E, NGRID, NYSEG, O&R, RG&E customers"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NY

    def formula(household, period, parameters):
        uncapped_incentive = 0
        p = parameters(
            period
        ).gov.states.ny.nysdps.clean_heat.clean_heat_others

        utility_provider = household("ny_clean_heat_utility_provider", period)
        category = household("ny_clean_heat_heat_pump_category", period)
        qualified_project_cost = household(
            "ny_clean_heat_project_cost", period
        )
        annual_energy_savings = household(
            "ny_clean_heat_annual_energy_savings", period
        )
        equipment_unit = household("ny_clean_heat_equipment_unit", period)
        heating_capacity = household("ny_clean_heat_heating_capacity", period)

        incentive_base = p.incentives_by_utility_others[utility_provider][
            category
        ]
        contractor_reward = p.contractor_reward[utility_provider][category]

        c = category.possible_values
        incentives_structure_energy_savings = [c.C4, c.C4A1, c.C4A2, c.C6]
        incentives_structure_equipment = [c.C5A, c.C5B, c.C7, c.C8]
        incentives_structure_heating_capacity = [c.C2, c.C2A, c.C2B, c.C2E]

        # Gas Soure Heat Pump category utilizes a special cap
        gshp_g3_incentive = min_(
            (incentive_base * (heating_capacity / 10000) - contractor_reward),
            p.gshp_c3_cap,
        )
        # Compute uncapped incentives based on category types
        uncapped_incentive = select(
            [
                category in incentives_structure_energy_savings,
                category in incentives_structure_equipment,
                category in incentives_structure_heating_capacity,
                category == category.possible_values.C3,
            ],
            [
                incentive_base * annual_energy_savings,
                incentive_base * equipment_unit,
                incentive_base * (heating_capacity / 10000),
                gshp_g3_incentive,
            ],
            default=0,
        )

        qualified_incentive = select(
            [
                category != category.possible_values.C3,
                category == category.possible_values.C3,
            ],
            [uncapped_incentive - contractor_reward, gshp_g3_incentive],
        )

        return min_(qualified_incentive, p.percentage * qualified_project_cost)
