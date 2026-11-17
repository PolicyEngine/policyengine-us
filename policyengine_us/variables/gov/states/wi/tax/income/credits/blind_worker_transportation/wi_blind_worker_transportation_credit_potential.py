from policyengine_us.model_api import *


class wi_blind_worker_transportation_credit_potential(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin blind-worker transportation credit before liability limit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.WI
    documentation = (
        "Sum of claimant-limited components on this tax return before applying "
        "the ordered nonrefundable credit limit. Each claimant's ceiling applies "
        "before aggregation."
    )
    reference = (
        "https://docs.legis.wisconsin.gov/statutes/statutes/71.pdf#page=56",
        # PDF pages 17-18.
        "https://www.revenue.wi.gov/TaxForms2025/2025-Form1-inst.pdf#page=17",
    )

    adds = ["wi_blind_worker_transportation_credit_person"]
