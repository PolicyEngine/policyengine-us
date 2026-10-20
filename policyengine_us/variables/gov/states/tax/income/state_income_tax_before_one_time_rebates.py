from policyengine_us.model_api import *


class state_income_tax_before_one_time_rebates(Variable):
    value_type = float
    entity = TaxUnit
    label = "State income tax before one-time rebates"
    documentation = (
        "State income tax plus state_income_tax_rebate_adjustment. This "
        "comparison output restores only registered rebates, including "
        "Colorado's residual TABOR sales tax refund and Massachusetts premium "
        "pay, while preserving ordinary refundable credits. It can be negative. "
        "It is an additive reconciliation holding other credit calculations "
        "and filing elections fixed, not a counterfactual recalculation of "
        "taxes with every rebate removed. Canonical state tax and household "
        "net income are unchanged. See docs/validation/state-rebates.md."
    )
    unit = USD
    definition_period = YEAR
    adds = ["state_income_tax", "state_income_tax_rebate_adjustment"]
