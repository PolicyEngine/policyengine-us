from policyengine_us.model_api import *


class is_ccdf_immigration_eligible_child(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Immigration eligibility for CCDF"
    reference = (
        "https://www.law.cornell.edu/uscode/text/8/1641",
        "https://www.law.cornell.edu/cfr/text/45/98.20",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.dhs.immigration
        immigration_status = person("immigration_status", period)
        immigration_status_str = immigration_status.decode_to_str()
        is_qualified_noncitizen = np.isin(
            immigration_status_str,
            p.qualified_noncitizen_status,
        )
        is_citizen = immigration_status == immigration_status.possible_values.CITIZEN
        return is_citizen | is_qualified_noncitizen
