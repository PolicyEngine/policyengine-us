from policyengine_us.model_api import *


class tx_tanf_immigration_status_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Eligible person for Texas Temporary Assistance for Needy Families (TANF) based on immigration status"
    definition_period = MONTH
    reference = (
        "https://www.hhs.texas.gov/handbooks/texas-works-handbook/part-a-determining-eligibility",
        "https://www.law.cornell.edu/uscode/text/8/1641",
    )
    defined_for = StateCode.TX

    def formula(person, period, parameters):
        p = parameters(period).gov.states.tx.tanf
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
