from policyengine_us.model_api import *


class ri_section_179_expense_add_back(Variable):
    value_type = float
    entity = TaxUnit
    label = "Rhode Island Section 179 expense add-back"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Rhode Island limits Section 179 depreciation to $25,000. "
        "If the federal return includes additional Section 179 depreciation "
        "under I.R.S. Code 179(b) beyond what was allowed prior to P.L. 119-21, "
        "H.R.1 (2025), that additional amount must be added back to federal AGI "
        "for Rhode Island purposes."
    )
    reference = (
        "https://tax.ri.gov/sites/g/files/xkgbur541/files/2025-12/2025%201040R%20Instructions%20122025.pdf#page=12",
        "http://webserver.rilin.state.ri.us/Statutes/title44/44-30/44-30-12.HTM",
    )
    defined_for = StateCode.RI
    # Other P.L. 119-21, H.R.1 (2025) add-backs NOT modeled (RI Schedule HR1):
    # - Business interest expense deduction [I.R.S. Code 163(j)]
    # - Section 174A Amortization Adjustment for R&E expenditures
    # - Qualified sound recording production deduction [I.R.S. Code 181]
