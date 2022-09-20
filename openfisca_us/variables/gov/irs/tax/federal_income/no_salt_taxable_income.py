from openfisca_us.model_api import *


class no_salt_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Federal taxable income if SALT were abolished"
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
            taxable_income = simulation.calculate("taxable_income", period)
            simulation.get_holder(
                "salt_deduction"
            ).variable.is_neutralized = False

        return taxable_income
