from policyengine_us.model_api import *


class ca_scc_general_assistance_age_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = (
        "Eligible for Santa Clara County General Assistance based on age requirements"
    )
    defined_for = "in_scc"
    reference = "https://stgenssa.sccgov.org/debs/program_handbooks/general_assistance/assets/01Policy/Policy.htm"

    def formula(person, period, parameters):
        p = parameters(period).gov.local.ca.scc.general_assistance
        age = person("monthly_age", period)
        return age >= p.age_threshold
