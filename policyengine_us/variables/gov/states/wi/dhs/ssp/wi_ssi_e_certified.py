from policyengine_us.model_api import *


class wi_ssi_e_certified(Variable):
    value_type = bool
    entity = Person
    label = "Certified for Wisconsin SSI Exceptional Expense Supplement"
    documentation = "County certification is effective in the requested month and ongoing SSI-E care requirements are met. Certification incorporates care needs, costs, approved placement or in-home services, and household support availability."
    definition_period = MONTH
    reference = "https://www.dhs.wisconsin.gov/publications/p20679-26-01.pdf"
