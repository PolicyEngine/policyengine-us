from policyengine_us.model_api import *


class cbo_household_federal_taxes(Variable):
    value_type = float
    entity = Household
    label = "CBO household federal taxes"
    documentation = (
        "Modeled federal taxes included in the PE-US CBO-style household "
        "income framework: individual income taxes plus employee, self-"
        "employment, employer-side federal payroll taxes, and any explicitly "
        "provided corporate or excise tax incidence."
    )
    definition_period = YEAR
    unit = USD
    adds = "gov.household.cbo_federal_taxes"
