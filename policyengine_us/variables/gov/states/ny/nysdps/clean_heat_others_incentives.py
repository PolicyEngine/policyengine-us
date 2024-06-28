from policyengine_us.model_api import *


class clean_heat_others_incentives(Variable):
    value_type = float
    entity = Household
    label = "NYS Clean Heat Program incentives for electric heat pump installation for CH&E, NGRID, NYSEG, O&R, RG&E customers"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        uncapped_incentive = 0
        p = parameters(period).gov.states.ny.nysdps.clean_heat

        utility_provider = tax_unit.household("utility_provider", period) # additional 25% for NG in selected zip code--implement or not?
        heat_pump_category = tax_unit.household("heat_pump_category", period)
        qualified_project_cost = tax_unit.household("clean_heat_project_cost", period)
        annual_energy_savings = tax_unit.household("clean_heat_annual_energy_savings", period)
        equipment_unit = tax_unit.household("clean_heat_equipment_unit", period)
        heating_capacity = tax_unit.household("clean_heat_heating_capacity", period)

        incentive_by_utility = p.incentives_by_utility_others
        contractor_reward = p.contractor_reward[utility_provider]

        incentive_base = incentive_by_utility[utility_provider][heat_pump_category]

        uncapped_incentive_energy_savings = incentive_base * annual_energy_savings - contractor_reward
        uncapped_incentive_equipment_unit = incentive_base * equipment_unit - contractor_reward
        uncapped_incentive_heating_capacity = incentive_base * (heating_capacity/10000) - contractor_reward
        
        uncapped_incentive = select(
            [
                heat_pump_category in p.incentives_structure_annual_energy_savings,
                heat_pump_category in p.incentives_structure_equipment_unit,
                heat_pump_category in p.incentives_structure_heating_capacity
            ],
            [
                uncapped_incentive_energy_savings,
                uncapped_incentive_equipment_unit,
                uncapped_incentive_heating_capacity,
            ],
        )

        uncapped_incentive = select(
            heat_pump_category == heat_pump_category.possible_values.C3, # if category C3, apply capped incentive if higher
            min_(uncapped_incentive, p.gshp_c3_cap)
            )

        return min_(uncapped_incentive, p.regular_project_cap * qualified_project_cost)