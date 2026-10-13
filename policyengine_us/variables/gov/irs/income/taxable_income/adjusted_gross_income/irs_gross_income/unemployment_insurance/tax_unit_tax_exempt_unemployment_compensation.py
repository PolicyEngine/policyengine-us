from policyengine_us.model_api import *


class tax_unit_tax_exempt_unemployment_compensation(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax-exempt unemployment compensation on the tax unit's return"
    unit = USD
    documentation = (
        "Unemployment compensation IRC 85(c) excludes from the AGI of the tax "
        "unit's return: the tax-exempt unemployment compensation of the "
        "members who are not dependents. A dependent's is excluded on the "
        "dependent's own return."
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/85#c"

    formula = sum_among_non_dependents("tax_exempt_unemployment_compensation")
