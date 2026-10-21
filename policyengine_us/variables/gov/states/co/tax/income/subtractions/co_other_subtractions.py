from policyengine_us.model_api import *


class co_other_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado other subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CO
    documentation = (
        "Colorado other subtractions from federal taxable income reported on "
        "Schedule DR 0104AD, line 20 in 2025 (line 23 in 2024), entered as a positive amount."
    )
    reference = (
        "https://tax.colorado.gov/sites/tax/files/documents/Book104_2025.pdf#page=23",
        "https://tax.colorado.gov/sites/tax/files/documents/DR0104_book_2024.pdf#page=23",
    )
