from policyengine_us.model_api import *


class mn_msa_countable_unearned_income(Variable):
    value_type = float
    entity = Person
    label = "Minnesota Supplemental Aid countable unearned income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MN
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/256D.44",
        "https://www.dhs.state.mn.us/main/groups/county_access/documents/pub/mndhs-073585.pdf#page=2",
    )

    def formula(person, period, parameters):
        # Per MN DHS Combined Manual 0018.18, MSA does not apply a
        # general unearned-income disregard separate from federal SSI's
        # $20 general disregard; the federal disregard is consumed
        # inside ssi_countable_income for the SSI track. MSA simply
        # treats unearned income (including the deemed-spouse amount)
        # as fully countable.
        return add(
            person,
            period,
            [
                "ssi_unearned_income",
                "ssi_unearned_income_deemed_from_ineligible_spouse",
            ],
        )
