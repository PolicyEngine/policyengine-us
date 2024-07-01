from policyengine_us.model_api import *


class clean_heat_others_incentives(Variable):
    value_type = float
    entity = Household
    label = "NYS Clean Heat Program incentives for electric heat pump installation for CH&E, NGRID, NYSEG, O&R, RG&E customers"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NY

    def formula(household, period, parameters):
        uncapped_incentive = 0
        p = parameters(period).gov.states.ny.nysdps.clean_heat

        utility_provider = household("utility_provider", period)
        category = household("heat_pump_category", period)
        qualified_project_cost = household("clean_heat_project_cost", period)
        annual_energy_savings = household("clean_heat_annual_energy_savings", period)
        equipment_unit = household("clean_heat_equipment_unit", period)
        heating_capacity = household("clean_heat_heating_capacity", period)

        incentive_base = p.incentives_by_utility_others[utility_provider][category]
        contractor_reward = p.contractor_reward[utility_provider][category]

        uncapped_incentive = select(
            [
                category == category.possible_values.C4 or \
                category == category.possible_values.C4A1 or \
                category == category.possible_values.C4A2 or \
                category == category.possible_values.C6,

                category == category.possible_values.C5A or \
                category == category.possible_values.C5B or \
                category == category.possible_values.C7 or \
                category == category.possible_values.C8,

                category == category.possible_values.C2 or \
                category == category.possible_values.C2A or \
                category == category.possible_values.C2B or \
                category == category.possible_values.C2E,

                category == category.possible_values.C3
            ],
            [
                incentive_base * annual_energy_savings - contractor_reward,
                incentive_base * equipment_unit - contractor_reward,
                incentive_base * (heating_capacity/10000) - contractor_reward,
                min_((incentive_base * (heating_capacity/10000) - contractor_reward), p.gshp_c3_cap)
            ],
        )

        return min_(uncapped_incentive, p.regular_project_cap * qualified_project_cost)