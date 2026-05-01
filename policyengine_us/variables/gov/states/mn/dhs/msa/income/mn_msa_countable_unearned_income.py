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
        "https://www.house.mn.gov/hrd/pubs/pap_MSA.pdf#page=3",
    )

    def formula(person, period, parameters):
        # MSA inherits the federal SSI $20 general income disregard. The
        # disregard applies first to unearned income; any unused remainder
        # rolls over to earned income (handled in
        # mn_msa_countable_earned_income).
        gross_unearned = add(
            person,
            period,
            [
                "ssi_unearned_income",
                "ssi_unearned_income_deemed_from_ineligible_spouse",
            ],
        )
        general = parameters(period).gov.states.mn.dhs.msa.disregard.general
        return max_(gross_unearned - general, 0)
