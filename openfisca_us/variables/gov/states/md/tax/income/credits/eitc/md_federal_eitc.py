from openfisca_us.model_api import *


class md_federal_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD modified federal EITC"
    unit = USD
    documentation = "The federal EITC with the minimum age condition ignored."
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        print("Calculating modified EITC")
        # Set up simulation clone
        simulation = tax_unit.simulation
        simulation.max_spiral_loops = 10
        simulation._check_for_cycle = lambda *args: None
        simulation_if_itemizing = simulation.clone()
        computed_variables = get_stored_variables(simulation)
        simulation_if_itemizing.tracer = simulation.tracer

        EITC_VARIABLES = [
            "eitc_agi_limit",
            "eitc_child_count",
            "eitc_eligible",
            "eitc_maximum",
            "eitc_phased_in",
            "eitc_reduction",
            "earned_income_tax_credit",
            "eitc",
        ]
        for variable in EITC_VARIABLES:
            simulation.get_holder(variable).delete_arrays()
        
        # Modify EITC age condition
        simulation.tax_benefit_system.parameters.gov.irs.credits.eitc.eligibility.age.min.update(
            value=0,
            period=period,
        )
        simulation.tax_benefit_system._parameters_at_instant_cache = {}
        eitc = simulation.calculate("eitc", period)

        # Ensure we don't modify any other variables
        added_variables = set(
            get_stored_variables(simulation_if_itemizing)
        ) - set(computed_variables)
        for variable in added_variables:
            simulation.get_holder(variable).delete_arrays()
        return eitc