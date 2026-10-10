from policyengine_us.model_api import *


class aca_tax_family_size(Variable):
    value_type = int
    entity = TaxUnit
    label = "Premium tax credit tax family size"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/36B#d_1",
        "https://www.law.cornell.edu/cfr/text/26/1.36B-1#d",
        "https://www.irs.gov/pub/irs-prior/i8962--2025.pdf#page=8",
    )
    documentation = (
        "Form 8962 line 1: the number of people in the premium tax credit "
        "tax family. It equals the tax unit size unless a head or spouse can "
        "be claimed as a dependent on another return, and is 0 when every "
        "head and spouse can be. The shared tax_unit_size is unchanged."
    )

    adds = ["is_aca_tax_family_member"]
