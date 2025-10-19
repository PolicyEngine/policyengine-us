from policyengine_us.model_api import *


class is_citizen_or_legal_immigrant(Variable):
    value_type = bool
    entity = Person
    label = "Is citizen or qualified noncitizen under federal law"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/8/1641"

    def formula(person, period, parameters):
        p = parameters(period).gov.dhs.immigration
        immigration_status = person("immigration_status", period)
        immigration_status_str = immigration_status.decode_to_str()
        is_citizen = (
            immigration_status == immigration_status.possible_values.CITIZEN
        )
        qualified_noncitizen = np.isin(
            immigration_status_str,
            p.qualified_noncitizen_status,
        )
        return qualified_noncitizen | is_citizen
