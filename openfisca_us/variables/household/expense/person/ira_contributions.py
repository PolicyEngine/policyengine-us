from openfisca_us.model_api import *


class ira_contributions(Variable):
    value_type = float
    entity = TaxUnit
    label = "IRA contributions"
    unit = USD
    documentation = "Contributions to Individual Retirement Accounts."
    definition_period = YEAR

