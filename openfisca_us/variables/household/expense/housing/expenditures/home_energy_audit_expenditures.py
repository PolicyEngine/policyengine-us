from openfisca_us.model_api import *


class home_energy_audit_expense(Variable):
    value_type = float
    entity = SPMUnit
    label = "Expenditures on home energy audits"
    unit = USD
    definition_period = YEAR
