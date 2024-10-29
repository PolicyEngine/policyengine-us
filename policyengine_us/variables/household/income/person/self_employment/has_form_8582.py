from policyengine_us.model_api import *


class has_form_8582(Variable):
    value_type = bool
    entity = Person
    label = "Person has filed form 8582"
    unit = USD
    reference = "https://www.irs.gov/pub/irs-pdf/f8582.pdf"
    definition_period = YEAR
