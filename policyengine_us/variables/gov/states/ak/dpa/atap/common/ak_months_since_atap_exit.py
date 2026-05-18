from policyengine_us.model_api import *


class ak_months_since_atap_exit(Variable):
    value_type = int
    entity = SPMUnit
    label = "Months since Alaska Temporary Assistance Program (ATAP) case closed"
    definition_period = MONTH
    defined_for = StateCode.AK
    reference = (
        {
            "title": "7 AAC 41.012(2) Parents achieving self-sufficiency (PASS) — PASS II transitional eligibility",
            "href": "https://www.akleg.gov/statutesPDF/aac%20Title%207.pdf#page=846",
        },
        {
            "title": "7 AAC 45 Alaska Temporary Assistance Program (ATAP) — chapter governing case closure timing",
            "href": "https://www.akleg.gov/statutesPDF/aac%20Title%207.pdf#page=1077",
        },
    )
