from policyengine_us.model_api import *


class co_other_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado other additions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CO
    documentation = "Other additions to federal taxable income reported on Colorado Form DR 0104, Line 2."
    reference = (
        "https://tax.colorado.gov/sites/tax/files/documents/DR0104_book_2024.pdf#page=9"
    )
