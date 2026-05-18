from policyengine_us.model_api import *


class ak_was_atap_recipient(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Was an Alaska Temporary Assistance Program (ATAP) recipient"
    definition_period = YEAR
    defined_for = StateCode.AK
    reference = (
        {
            "title": "7 AAC 41.012(2) Parents achieving self-sufficiency (PASS) — PASS II transitional eligibility",
            "href": "https://www.akleg.gov/statutesPDF/aac%20Title%207.pdf#page=846",
        },
        {
            "title": "7 AAC 45 Alaska Temporary Assistance Program (ATAP) — chapter governing recipient determination",
            "href": "https://www.akleg.gov/statutesPDF/aac%20Title%207.pdf#page=1077",
        },
    )
