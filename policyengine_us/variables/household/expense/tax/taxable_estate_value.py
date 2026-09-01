from policyengine_us.model_api import *


class taxable_estate_value(Variable):
    value_type = float
    entity = Person
    label = "Taxable estate value"
    unit = USD
    documentation = (
        "Taxable estate under IRC § 2051 (gross estate less deductions) on "
        "which the § 2001(c) tentative tax is computed. This is a household "
        "calculator input only: no PolicyEngine dataset populates it (checked "
        "against policyengine-us-data and Microcosm on 2026-09-01), so the "
        "estate tax is zero in every microsimulation."
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/2051"
