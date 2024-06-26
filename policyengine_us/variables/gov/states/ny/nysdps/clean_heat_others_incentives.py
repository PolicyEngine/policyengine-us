from policyengine_us.model_api import *


class clean_heat_others_incentives(Variable):
    value_type = float
    entity = Household
    label = "NYS Clean Heat Program incentives for electric heat pump installation for CH&E, NGRID, NYSEG, O&R, RG&E customers"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NY
    hidden_input = True # what is this for?

    def formula(tax_unit, period, parameters):
        uncapped_incentive = 0
        p = parameters(period).gov.states.ny.nysdps.clean_heat # do we need to run simulation or select(), if so, why?

        utility_provider = tax_unit.household("utility_provider", period)
        heatpump_category = tax_unit.household("heat_pump_category", period)
        qualified_project_cost = tax_unit.household("clean_heat_project_cost", period)
        annual_energy_savings = tax_unit.household("clean_heat_annual_energy_savings", period) # how to make this visible for selected heatpump category on frontend?
        equipment_unit = tax_unit.household("clean_heat_equipment_unit", period) # same comment as above
        heating_capacity = tax_unit.household("clean_heat_heating_capacity", period) # same comment as above
        tier = tax_unit.household("clean_heat_c4a_tier", period)

        incentive_by_utility = p.incentives_by_utility_others
        contractor_reward = p.contractor_reward

        incentive_base = index_(
            into=incentive_by_utility,
            indices=[utility_provider, heatpump_category, tier]) # tier only exists for c4a, to check if indexing like this would work
        
        contractor_reward = index_(
            into=contractor_reward,
            indices=[utility_provider, heatpump_category])

        if heatpump_category in tax_unit.household("incentives_structure_annual_energy_savings", period): # can we use if statement here?
            uncapped_incentive = incentive_base * annual_energy_savings - contractor_reward
        if heatpump_category in tax_unit.household("incentives_structure_equipment_unit", period):
            uncapped_incentive = incentive_base * equipment_unit - contractor_reward
        else: 
            uncapped_incentive = incentive_base * (heating_capacity/10000) - contractor_reward

        if heatpump_category.status == "GSHP: Full Load Heating": # static var like this ok? how to link and point it to GSHP C3?
            uncapped_incentive = min_(uncapped_incentive, p.gshp_c3_cap)
        
        return min_(uncapped_incentive, p.regular_project_cap * qualified_project_cost)