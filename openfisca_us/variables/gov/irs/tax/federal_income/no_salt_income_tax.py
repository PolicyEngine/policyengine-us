from openfisca_us.model_api import *


class no_salt_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Federal income tax if SALT were abolished"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        with BranchedSimulation(tax_unit) as simulation:
            simulation.tax_benefit_system.neutralize_variable("salt_deduction")
            simulation.get_holder(
                "salt_deduction"
            ).variable = simulation.tax_benefit_system.variables[
                "salt_deduction"
            ]  # This is needed because neutralize_variable is only designed to work *before* simulations have started.
            tax_liability = simulation.calculate("income_tax", period)
            simulation.get_holder(
                "salt_deduction"
            ).variable.is_neutralized = False

        return tax_liability
