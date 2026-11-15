from policyengine_us.model_api import *


class wi_blind_worker_qualifying_transportation_expenses(Variable):
    value_type = float
    entity = Person
    label = "Wisconsin blind-worker qualifying transportation expenses"
    unit = USD
    definition_period = YEAR
    default_value = 0
    documentation = (
        "Annual uncapped qualified amount paid by this claimant for mass transit, "
        "paratransit, taxicab or transportation network company services between "
        "home and work. Supply the net amount after excluding reimbursements and "
        "ABLE-funded payments tied to a related Wisconsin contribution subtraction "
        "claimed by the account owner or another depositor. This input does not "
        "classify receipts, derive qualified amounts from generic work expenses "
        "or allocate mixed funding. Its zero default does not verify zero expense."
    )
    reference = (
        "https://docs.legis.wisconsin.gov/statutes/statutes/71.pdf#page=56",
        # PDF pages 17-18.
        "https://www.revenue.wi.gov/TaxForms2025/2025-Form1-inst.pdf#page=17",
    )
