from policyengine_us.model_api import *


class mn_msa_earned_income_disregard(Variable):
    value_type = float
    entity = Person
    label = "Minnesota Supplemental Aid earned income disregard"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MN
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/256D.44",
        "https://www.dhs.state.mn.us/main/groups/county_access/documents/pub/mndhs-073585.pdf#page=2",
    )

    def formula(person, period, parameters):
        # Per MN DHS Combined Manual 0018.18, MSA's non-SSI track
        # disregards the first $65 of earned income plus half the
        # remainder. The federal $20 general-income disregard belongs
        # to the SSI track's own countable-income calculation, not
        # to MSA — see ssi_countable_income.
        p = parameters(period).gov.states.mn.dhs.msa.disregard.earned
        gross_earned = add(
            person,
            period,
            [
                "ssi_earned_income",
                "ssi_earned_income_deemed_from_ineligible_spouse",
            ],
        )
        initial_disregard = min_(gross_earned, p.initial)
        remainder = max_(gross_earned - p.initial, 0)
        return initial_disregard + remainder * p.rate
