from policyengine_us.model_api import *


class mn_special_refund_qualifying_claimant(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Minnesota special refund claimant meets the remaining non-income claim conditions"
    definition_period = YEAR
    # Attests qualifying homestead/residency, no disqualifying delinquency or
    # relative homestead, and other M1PR conditions. Income is not a restriction.
    # Dependency is also checked separately by mn_special_refund_eligible.
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/290A.03#stat.290A.03.8",
        "https://www.revenue.state.mn.us/sites/default/files/2026-03/m1prsr-25.pdf#page=2",
    )
