from policyengine_us.model_api import *


class mn_msa_assistance_standard(Variable):
    value_type = float
    entity = Person
    label = "Minnesota Supplemental Aid assistance standard"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MN
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/256D.44",
        "https://www.dhs.state.mn.us/main/groups/county_access/documents/pub/mndhs-073585.pdf#page=4",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mn.dhs.msa.assistance_standard
        arrangement = person("mn_msa_payment_category", period)
        return p.amount[arrangement]
