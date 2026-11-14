from policyengine_us.model_api import *


class mn_homestead_credit_refund_qualified_property_taxes(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota Homestead Credit Refund qualified taxes payable in the following year"
    unit = USD
    definition_period = YEAR
    default_value = -1
    # Claim-income year 2025 uses M1PR line 14 from the taxes-payable-2026
    # statement, including applicable mobile-home and home-use worksheets.
    # Assign the qualified claim amount once. Current-year paid real_estate_taxes
    # remain separate SALT/expense inputs and are not a substitute for this bill.
    # Enter an actual zero when known; -1 means the qualified amount is unknown.
    reference = (
        # PDF pages 9, 12
        "https://www.revenue.state.mn.us/sites/default/files/2026-06/m1pr-inst-25.pdf#page=9",
        "https://www.revenue.state.mn.us/sites/default/files/2026-06/m1pr-25.pdf#page=2",
        "https://www.revisor.mn.gov/statutes/cite/290A.03#stat.290A.03.13",
    )
