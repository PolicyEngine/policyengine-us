from openfisca_us.model_api import *


class is_ssi_recipient_for_medicaid(Variable):
    value_type = bool
    entity = Person
    label = "Is an SSI recipient for Medicaid"
    documentation = "Qualifies for Medicaid due to receiving SSI, or if in a 209(b) state, due to meeting that state's eligibility requirements."
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/42/1396a#f"

    def formula(person, period, parameters):
        state = person.household("state_code_str", period)
        ma = parameters(period).hhs.medicaid.eligibility.categories
        is_covered = ma.ssi_recipient.is_covered[state] > 0
        receives_ssi = person("ssi", period) > 0
        return receives_ssi & is_covered
