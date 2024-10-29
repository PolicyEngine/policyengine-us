from policyengine_us.model_api import *


class passive_losses_allowed(Variable):
    value_type = bool
    entity = Person
    label = "Whether passive losses are allowed"
    unit = USD
    reference = "https://www.irs.gov/pub/irs-pdf/f8582.pdf"
    definition_period = YEAR
