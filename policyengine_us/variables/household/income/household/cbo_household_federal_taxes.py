from policyengine_us.model_api import *


class cbo_household_federal_taxes(Variable):
    value_type = float
    entity = Household
    label = "CBO household federal taxes"
    documentation = (
        "Federal taxes included in the CBO household income framework: "
        "individual income taxes, payroll taxes, corporate income taxes, "
        "and excise taxes."
    )
    definition_period = YEAR
    unit = USD
    adds = "gov.household.cbo_federal_taxes"
