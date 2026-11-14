from policyengine_us.model_api import *


class wi_veterans_property_tax_credit_claim_permitted(Variable):
    """This actual claim is timely and free of an applicable claim disqualification.

    A documented authorized extension may establish timeliness. Do not infer an
    extension, annual recertification or absence of a refundable-credit claim bar
    merely because the underlying property and military facts qualify.
    """

    value_type = bool
    entity = TaxUnit
    label = "Wisconsin veterans property tax credit claim is permitted"
    definition_period = YEAR
    reference = (
        "https://docs.legis.wisconsin.gov/statutes/statutes/71/i/07/6e",
        # PDF pages 27-30
        "https://www.revenue.wi.gov/TaxForms2025/2025-Form1-Inst.pdf#page=27",
    )
