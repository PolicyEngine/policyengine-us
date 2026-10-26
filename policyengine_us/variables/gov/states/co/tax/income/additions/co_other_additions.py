from policyengine_us.model_api import *


class co_other_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado other additions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CO
    documentation = (
        "Colorado other additions to federal taxable income reported on "
        "Form DR 0104, line 9 in 2025 (line 8 in 2024), entered as a positive amount."
    )
    reference = (
        # PDF pages 9-10
        "https://tax.colorado.gov/sites/tax/files/documents/Book104_2025.pdf#page=9",
        "https://tax.colorado.gov/sites/tax/files/documents/DR0104_book_2024.pdf#page=10",
    )
