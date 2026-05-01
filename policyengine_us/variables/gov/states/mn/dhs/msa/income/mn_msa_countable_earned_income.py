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
        gross_earned = add(
            person,
            period,
            [
                "ssi_earned_income",
                "ssi_earned_income_deemed_from_ineligible_spouse",
            ],
        )
        disregard = person("mn_msa_earned_income_disregard", period)
        return max_(gross_earned - disregard, 0)
