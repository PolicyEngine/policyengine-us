from policyengine_us.model_api import *


class medicaid_working_disabled_buy_in_premium_person(Variable):
    value_type = float
    entity = Person
    label = "Medicaid working disabled Buy-In monthly premium per person"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.dhcs.ca.gov/services/working-disabled-program/",
        "https://hfs.illinois.gov/medicalprograms/hbwd/premiums.html",
    )

    adds = [
        "ca_wdp_premium",
        "il_hbwd_premium",
    ]
