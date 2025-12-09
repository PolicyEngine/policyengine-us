from policyengine_us.model_api import *


class il_bcc_age_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Illinois Health Benefits for Persons with Breast or Cervical Cancer age eligible"
    definition_period = YEAR
    reference = ("https://www.dhs.state.il.us/page.aspx?item=33528",)
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        p = parameters(period).gov.states.il.hfs.bcc.eligibility
        age = person("age", period)
        return age < p.age
