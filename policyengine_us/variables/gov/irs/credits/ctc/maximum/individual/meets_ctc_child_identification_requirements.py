from policyengine_us.model_api import *


class meets_ctc_child_identification_requirements(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Child meets CTC identification requirements"
    reference = "https://www.law.cornell.edu/uscode/text/26/24#h_7"

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.credits.ctc
        if p.child_ssn_requirement_applies:
            ssn_card_type = person("ssn_card_type", period)
            ssn_card_str = ssn_card_type.decode_to_str()
            p = parameters(period).gov.irs.credits.ctc
            return np.isin(ssn_card_str, p.eligible_ssn_card_type)
        return True
