from policyengine_us.model_api import *


class taxable_estate_value(Variable):
    value_type = float
    entity = Person
    label = "Taxable estate value"
    unit = USD
    documentation = (
        "Taxable estate under section 2051 (gross estate less the deductions "
        "in sections 2053 through 2058) on which the section 2001(c) "
        "tentative tax is computed. This is a household calculator input: no "
        "PolicyEngine dataset populates it (policyengine-us-data and "
        "Microcosm checked on 2026-09-01), so estate_tax is zero in every "
        "microsimulation."
    )
    quantity_type = STOCK
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/2051",
        "https://www.law.cornell.edu/uscode/text/26/2001#b_1",
    )
