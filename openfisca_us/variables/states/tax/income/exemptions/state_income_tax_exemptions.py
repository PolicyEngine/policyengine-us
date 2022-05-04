from openfisca_us.model_api import *


class state_income_tax_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "State income tax exemptions"
    unit = USD
    definition_period = YEAR

    formula = sum_of_variables(
        [
            "state_income_tax_personal_exemption",
            "state_income_tax_dependent_exemption",
            "state_income_tax_aged_exemption",
            "state_income_tax_blind_exemption",
        ]
    )
