from policyengine_us.model_api import *


class tax_unit_taxable_unemployment_compensation(Variable):
    value_type = float
    entity = TaxUnit
    label = "Taxable unemployment compensation"
    unit = USD
    documentation = (
        "Unemployment compensation included in AGI: the taxable unemployment "
        "compensation of the members who are not dependents. A dependent's "
        "compensation is on the dependent's own return."
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/85"

    formula = sum_among_non_dependents("taxable_unemployment_compensation")
