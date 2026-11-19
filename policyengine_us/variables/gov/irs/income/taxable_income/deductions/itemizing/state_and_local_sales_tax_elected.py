from policyengine_us.model_api import *


class state_and_local_sales_tax_elected(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Elect state and local general sales taxes on federal Schedule A"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/164#b_5"

    def formula(tax_unit, period, parameters):
        # An input with only the total has historically represented income tax
        # for Virginia. A filer can supply the election with the total.
        simulation = tax_unit.simulation
        if any(
            ("state_and_local_sales_or_income_tax", branch, period)
            in simulation._user_input_keys
            for branch in simulation._get_visible_branch_names()
        ):
            return False
        income_tax = add(
            tax_unit, period, ["state_withheld_income_tax", "local_income_tax"]
        )
        sales_tax = add(tax_unit, period, ["state_sales_tax", "local_sales_tax"])
        return sales_tax > income_tax
