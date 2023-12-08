from policyengine_us.model_api import *


class va_agi_less_exemptions_person(Variable):
    value_type = float
    entity = Person
    label = "Difference between individual VAGI and personal exemption amounts"
    defined_for = StateCode.VA
    unit = USD
    definition_period = YEAR
    reference = "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=19"

    adds = ["va_agi_person"]
    subtracts = [
        "va_aged_blind_exemption_person",
        "va_personal_exemption_person",
    ]
