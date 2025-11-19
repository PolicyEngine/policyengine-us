from policyengine_us.model_api import *


class il_hbwd_age_eligible(Variable):
    value_type = bool
    entity = Person
    label = (
        "Illinois Health Benefits for Workers with Disabilities age eligible"
    )
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-120.510",
        "https://hfs.illinois.gov/medicalprograms/hbwd/eligibility.html",
    )
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        p = parameters(period).gov.states.il.hfs.hbwd.eligibility
        age = person("monthly_age", period)
        return p.age.calc(age)
