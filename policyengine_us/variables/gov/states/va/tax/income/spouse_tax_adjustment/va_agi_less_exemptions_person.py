from policyengine_us.model_api import *


class va_agi_less_exemptions_person(Variable):
    value_type = float
    entity = Person
    label = "Difference between individual VAGI and personal exemption amounts"
    defined_for = StateCode.VA
    unit = USD
    definition_period = YEAR
    reference = "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=19"

    def formula(person, period, parameters):
        # Get the individual's VAGI.
        va_agi = person("va_agi_person", period)

        # Get the individual's personal exemption amount.
        personal_exemption = person("va_personal_exemption_person", period)

        # Get the individual's aged/blind exemption amount.
        aged_blind_exemption = person("va_aged_blind_exemption_person", period)

        # Subtract the exemptions from the VAGI.
        return max_(va_agi - personal_exemption - aged_blind_exemption, 0)
