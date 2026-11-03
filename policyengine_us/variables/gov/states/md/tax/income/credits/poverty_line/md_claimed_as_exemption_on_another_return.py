from policyengine_us.model_api import *


class md_claimed_as_exemption_on_another_return(Variable):
    value_type = bool
    entity = Person
    label = "Claimed as an exemption on another Maryland return"
    documentation = (
        "Whether another individual actually claims this person as an "
        "exemption on a Maryland return under Tax-General 10-211. Being "
        "claimable is not enough, and a claim on a federal return alone does "
        "not establish it."
    )
    definition_period = YEAR
    defined_for = StateCode.MD
    reference = "https://mgaleg.maryland.gov/mgawebsite/Laws/StatuteText?article=gtg&section=10-709&enactments=false"
