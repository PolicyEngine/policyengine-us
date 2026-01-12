from policyengine_us.model_api import *


class il_fpp_income_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Illinois Family Planning Program income eligible"
    definition_period = YEAR
    reference = (
        "https://www.dhs.state.il.us/page.aspx?item=146077",
        "https://hfs.illinois.gov/medicalclients/familyplanning.html",
    )
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        p = parameters(period).gov.states.il.hfs.fpp.eligibility
        income_level = person("il_fpp_income_level", period)
        return income_level <= p.income_limit
