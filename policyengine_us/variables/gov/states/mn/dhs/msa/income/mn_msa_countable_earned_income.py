from policyengine_us.model_api import *


class mn_msa_countable_earned_income(Variable):
    value_type = float
    entity = Person
    label = "Minnesota Supplemental Aid countable earned income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MN
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/256D.44",
        "https://www.dhs.state.mn.us/main/groups/county_access/documents/pub/mndhs-073585.pdf#page=2",
    )

    def formula(person, period, parameters):
        # Per MN DHS Combined Manual 0018.18: "For SSI recipients, no
        # county action is required. For non-SSI recipients due to
        # excess income, disregard the 1st $65 of earned income plus
        # half of the remaining earned income." For SSI-track recipients
        # the federal $20 + $65 + 1/2 disregards are already consumed
        # inside ssi_countable_income, so MSA-side earned income is
        # treated as fully disregarded (returned as 0) to avoid
        # double-counting.
        gross_earned = add(
            person,
            period,
            [
                "ssi_earned_income",
                "ssi_earned_income_deemed_from_ineligible_spouse",
            ],
        )
        disregard = person("mn_msa_earned_income_disregard", period)
        non_ssi_track_countable = max_(gross_earned - disregard, 0)
        receives_ssi = person("ssi", period) > 0
        return where(receives_ssi, 0, non_ssi_track_countable)
