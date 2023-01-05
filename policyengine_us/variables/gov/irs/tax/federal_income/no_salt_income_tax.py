from policyengine_us.model_api import *


class no_salt_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Federal income tax if SALT were abolished"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        simulation = tax_unit.simulation
        no_salt_branch = simulation.get_branch("no_salt")
        no_salt_branch.set_input(
            "salt_deduction", period, np.zeros(tax_unit.count)
        )
        return no_salt_branch.calculate("income_tax", period)
