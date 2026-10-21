from policyengine_us.model_api import *


class state_income_tax_rebate_adjustment(Variable):
    value_type = float
    entity = TaxUnit
    label = "State income tax rebate adjustment"
    documentation = (
        "Registered rebate amounts actually included in modeled state income "
        "tax for this year, including Colorado's residual TABOR sales tax "
        "refund and Massachusetts premium pay. Nonrefundable amounts reflect "
        "remaining liability and any subsequent spouse adjustment. Ordinary "
        "credits, other credit bases and filing elections remain fixed. "
        "The dated registry defines coverage; see docs/validation/state-rebates.md."
    )
    unit = USD
    definition_period = YEAR
    adds = "gov.states.household.state_income_tax_rebate_adjustments"
