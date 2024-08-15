from policyengine_us.model_api import *


class ne_involved_in_adc_employment_first(Variable):
    value_type = bool
    entity = Person
    label = (
        "Involved with Nebraska Employment First as part of the ADC program"
    )
    definition_period = YEAR
    reference = (
        "https://www.clasp.org/sites/default/files/public/resources-and-publications/publication-1/Nebraskas-Employment-First-Program-2.pdf",
    )
    defined_for = StateCode.NE
