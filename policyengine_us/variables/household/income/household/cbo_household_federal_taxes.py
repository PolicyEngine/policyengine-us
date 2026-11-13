from policyengine_us.model_api import *


class cbo_household_federal_taxes(Variable):
    value_type = float
    entity = Household
    label = "CBO household federal taxes"
    documentation = (
        "Modeled federal taxes included in the PE-US CBO-style household "
        "income framework: individual income taxes net of refundable credits, "
        "including the premium tax credit, plus employee, self-employment and "
        "employer-side federal payroll taxes, and any explicitly provided "
        "corporate or excise tax incidence."
    )
    definition_period = YEAR
    unit = USD
    adds = "gov.household.cbo_federal_taxes"
    subtracts = "gov.household.cbo_federal_tax_subtractions"
