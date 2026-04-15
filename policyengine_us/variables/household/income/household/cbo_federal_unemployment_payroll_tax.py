from policyengine_us.model_api import *


class cbo_federal_unemployment_payroll_tax(Variable):
    value_type = float
    entity = Household
    label = "Allocated federal unemployment payroll tax for CBO household income"
    documentation = (
        "Household federal unemployment insurance payroll tax used in the "
        "CBO household income framework."
    )
    definition_period = YEAR
    unit = USD
