from policyengine_us.model_api import *


class mn_msa_countable_income(Variable):
    value_type = float
    entity = Person
    label = "Minnesota Supplemental Aid countable income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MN
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/256D.44",
        "https://www.dhs.state.mn.us/main/groups/county_access/documents/pub/mndhs-073585.pdf#page=2",
    )

    adds = [
        "mn_msa_countable_earned_income",
        "mn_msa_countable_unearned_income",
    ]
