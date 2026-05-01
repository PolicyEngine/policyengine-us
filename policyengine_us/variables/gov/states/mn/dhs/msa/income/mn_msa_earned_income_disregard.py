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
        # remainder. The federal $20 general disregard also applies on
        # the non-SSI track (per House Research and CM 0018.18); it
        # consumes unearned income first and any leftover rolls into
        # this earned-income calculation.
        p = parameters(period).gov.states.mn.dhs.msa.disregard
        gross_unearned = add(
            person,
            period,
            [
                "ssi_unearned_income",
                "ssi_unearned_income_deemed_from_ineligible_spouse",
            ],
        )
        gross_earned = add(
            person,
            period,
            [
                "ssi_earned_income",
                "ssi_earned_income_deemed_from_ineligible_spouse",
            ],
        )
        leftover_general = max_(p.general - gross_unearned, 0)
        flat = p.earned.initial + leftover_general
        flat_disregard = min_(gross_earned, flat)
        remainder = max_(gross_earned - flat, 0)
        return flat_disregard + remainder * p.earned.rate
