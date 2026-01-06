from policyengine_us.model_api import *


class az_adoption_expenses(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona qualifying adoption expenses"
    unit = USD
    documentation = (
        "Unreimbursed medical and hospital costs, adoption counseling fees, "
        "legal fees, agency fees, and other nonrecurring costs of adoption."
    )
    definition_period = YEAR
