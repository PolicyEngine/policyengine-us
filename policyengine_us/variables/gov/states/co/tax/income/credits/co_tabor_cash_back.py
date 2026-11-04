from policyengine_us.model_api import *


class co_tabor_cash_back(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado TABOR cash back"
    documentation = (
        "One-time Colorado Cash Back payment under SB 22-233, paid in 2022 and based "
        "on the 2021 return. PolicyEngine attributes it to the 2021 eligibility year "
        "through co_refundable_credits. The amount is zero outside 2021. It is "
        "separate from co_sales_tax_refund."
    )
    defined_for = StateCode.CO
    unit = USD
    definition_period = YEAR
    reference = (
        "https://leg.colorado.gov/sites/default/files/2022a_233_signed.pdf#page=3",
        "https://leg.colorado.gov/sites/default/files/documents/2022A/bills/fn/2022a_sb233_f1.pdf#page=2",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.co.tax.income.credits.tabor

        joint = tax_unit("tax_unit_is_joint", period)
        return where(joint, p.joint, p.single)
