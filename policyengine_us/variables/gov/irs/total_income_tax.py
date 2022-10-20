from policyengine_us.model_api import *


class federal_state_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Total federal and state income tax"
    unit = USD
    definition_period = YEAR

    formula = sum_of_variables(["income_tax", "state_income_tax"])
