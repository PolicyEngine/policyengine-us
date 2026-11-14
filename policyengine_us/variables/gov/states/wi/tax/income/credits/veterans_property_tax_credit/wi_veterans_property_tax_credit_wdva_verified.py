from policyengine_us.model_api import *


class wi_veterans_property_tax_credit_wdva_verified(Variable):
    """WDVA verification supports this claimant and the credited effective periods.

    Continuing valid certification need not be reissued annually. With known
    legal facts, false is a verified failure; otherwise it is only a default.
    Generic veteran status, disability or a historical rating is insufficient.
    """

    value_type = bool
    entity = TaxUnit
    label = "Wisconsin veterans property tax credit WDVA verification"
    definition_period = YEAR
    reference = (
        "https://docs.legis.wisconsin.gov/statutes/statutes/71/i/07/6e",
        "https://www.revenue.wi.gov/TaxForms2025/2025-Form1-Inst.pdf#page=30",
    )
