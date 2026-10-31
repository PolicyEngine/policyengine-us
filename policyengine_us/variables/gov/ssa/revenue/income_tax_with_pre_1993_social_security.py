from policyengine_us.model_api import *
from policyengine_us.tools.tob import income_tax_with_social_security_override


class income_tax_with_pre_1993_social_security(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Income tax with pre-1993 taxable Social Security"
    unit = USD
    documentation = (
        "Cached income-tax counterfactual using the pre-1993 section 86 "
        "includible amount under current income-tax rules. The counterfactual "
        "branch is released after calculating income tax."
    )

    def formula(tax_unit, period, parameters):
        taxable_social_security = tax_unit(
            "tax_unit_taxable_social_security_pre_1993", period
        )
        return income_tax_with_social_security_override(
            tax_unit.simulation,
            period,
            taxable_social_security=taxable_social_security,
        )
