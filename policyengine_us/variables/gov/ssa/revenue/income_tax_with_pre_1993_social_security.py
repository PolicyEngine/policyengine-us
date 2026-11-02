from policyengine_us.model_api import *
from policyengine_us.tools.tob import income_tax_with_social_security_override


class income_tax_with_pre_1993_social_security(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Chapter 1 income tax with bounded pre-1993 taxable Social Security"
    unit = USD
    documentation = (
        "Cached chapter 1 income-tax counterfactual (after nonrefundable and "
        "before refundable credits, excluding chapter 2A net investment "
        "income tax) using the lesser of the pre-1993 section 86 includible "
        "amount and actual inclusion, under current income-tax rules. The "
        "counterfactual branch is released after calculating the tax."
    )
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/401",
        "https://www.ssa.gov/OP_Home/comp2/F098-021.html",
    )

    def formula(tax_unit, period, parameters):
        # Read actual inclusion here, before any branch neutralizes it.
        taxable_social_security = min_(
            tax_unit("tax_unit_taxable_social_security_pre_1993", period),
            tax_unit("tax_unit_taxable_social_security", period),
        )
        return income_tax_with_social_security_override(
            tax_unit.simulation,
            period,
            taxable_social_security=taxable_social_security,
        )
