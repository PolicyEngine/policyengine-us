from policyengine_us.model_api import *


class co_other_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado other subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CO
    documentation = "Other subtractions from federal taxable income reported on Colorado Form DR 0104, Line 4 / Subtractions Schedule DR 0104AD."
    reference = "https://tax.colorado.gov/sites/tax/files/documents/DR0104_book_2024.pdf#page=18"
