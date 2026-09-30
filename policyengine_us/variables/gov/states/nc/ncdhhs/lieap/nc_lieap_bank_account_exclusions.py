from policyengine_us.model_api import *


class nc_lieap_bank_account_exclusions(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    quantity_type = STOCK
    unit = USD
    label = "North Carolina LIEAP excluded bank-account funds"
    documentation = (
        "The portion of reported bank balances excluded under EP-300.11: "
        "outstanding withdrawals and funds still in the accounts that were "
        "counted as income in the LIEAP application. Report the combined "
        "exclusion without double counting overlapping amounts. These offsets "
        "cannot reduce cash or lump sums held outside bank accounts."
    )
    reference = (
        "https://policies.ncdhhs.gov/wp-content/uploads/EP-300-5.1.2026.pdf#page=17,18"
    )
