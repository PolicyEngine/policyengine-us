from policyengine_us.model_api import *


class cbo_household_federal_taxes(Variable):
    value_type = float
    entity = Household
    label = "CBO household federal taxes"
    documentation = (
        "Modeled federal taxes included in the PE-US CBO-style household "
        "income framework: individual income taxes plus employee, self-"
        "employment, and employer-side federal payroll taxes. Corporate and "
        "excise tax incidence are excluded until they are explicitly "
        "allocated to households."
    )
    definition_period = YEAR
    unit = USD
    adds = "gov.household.cbo_federal_taxes"
