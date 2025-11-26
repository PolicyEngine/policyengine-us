from policyengine_us.model_api import *


class is_ca_medicaid_immigration_status_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for California state-funded Medicaid regardless of immigration status"
    definition_period = YEAR
    reference = [
        "https://california.public.law/codes/welfare_and_institutions_code_section_14007.8",
    ]
    defined_for = StateCode.CA

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ca.chhs
        age = person("age", period)
        pregnant = person("is_pregnant", period)
        return p.eligible_regardless_of_immigration_status.calc(age) | pregnant
