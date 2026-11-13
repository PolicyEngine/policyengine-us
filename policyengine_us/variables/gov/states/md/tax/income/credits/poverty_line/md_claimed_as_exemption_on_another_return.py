from policyengine_us.model_api import *


class md_claimed_as_exemption_on_another_return(Variable):
    value_type = bool
    entity = Person
    label = "Claimed as an exemption on another Maryland return"
    documentation = (
        "Whether another individual actually claims this person as an "
        "exemption on a Maryland return under Tax-General 10-211. Being "
        "claimable is not enough. Defaults to an actual claim on another "
        "federal return, since a Maryland claimant takes an exemption for "
        "each IRC 152 dependent; set it to false when the claimant files no "
        "Maryland return."
    )
    definition_period = YEAR
    defined_for = StateCode.MD
    reference = (
        "https://mgaleg.maryland.gov/mgawebsite/Laws/StatuteText?article=gtg&section=10-709&enactments=false",
        "https://mgaleg.maryland.gov/mgawebsite/Laws/StatuteText?article=gtg&section=10-211&enactments=false",
    )

    def formula(person, period, parameters):
        return person("claimed_as_dependent_on_another_return", period)
