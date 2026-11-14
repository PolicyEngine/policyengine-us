from policyengine_us.model_api import *


class wi_veterans_property_tax_credit_qualified_property_taxes(Variable):
    """Full unrounded municipal-received qualified net tax for this credit year.

    Supply a traceable payment ledger after existing bill credits and lawful
    principal-property, business, acreage, ownership and closing allocations.
    Include qualified municipal mobile-home fees or documented direct-tax rent
    only for source-supported effective periods. Unknown or disputed facts are
    unavailable; this input does not resolve acreage or midyear rating conflicts.
    It is not a precomputed credit, generic taxes paid or an income-tax refund.
    """

    value_type = float
    entity = TaxUnit
    label = "Wisconsin veterans property tax credit qualified property taxes"
    definition_period = YEAR
    unit = USD
    default_value = -1
    reference = (
        "https://docs.legis.wisconsin.gov/statutes/statutes/71/i/07/6e",
        # PDF pages 28-30
        "https://www.revenue.wi.gov/TaxForms2025/2025-Form1-Inst.pdf#page=28",
    )
