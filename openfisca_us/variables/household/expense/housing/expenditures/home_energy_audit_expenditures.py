from openfisca_us.model_api import *


class home_energy_audit_expenditures(Variable):
    value_type = float
    entity = TaxUnit
    label = "Expenditures on home energy audits"
    unit = USD
    definition_period = YEAR
    question = "How much do you spend on home energy audits?"
