from policyengine_us.model_api import *


class meets_ctc_identification_requirements(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Person meets CTC identification requirements"
    reference = (
        "https://www.congress.gov/bill/119th-congress/house-bill/1/text"
    )

    def formula(person, period, parameters):
        ssn_card_type = person("ssn_card_type", period)
        ssn_card_str = ssn_card_type.decode_to_str()
        p = parameters(period).gov.irs.credits.ctc
        return np.isin(ssn_card_str, p.eligible_ssn_card_type)
