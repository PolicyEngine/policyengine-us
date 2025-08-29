from policyengine_us.model_api import *


class boost_tax(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "BOOST Act supplemental tax"
    unit = USD
    documentation = "Supplemental tax on AGI to fund the BOOST Act"
    reference = "placeholder - bill not yet introduced"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.contrib.congress.tlaib.income_security_package.boost_act

        if not p.in_effect:
            return tax_unit("adjusted_gross_income", period) * 0

        agi = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)

        threshold = p.tax.threshold[filing_status]
        rate = p.tax.rate

        excess_agi = max_(agi - threshold, 0)
        tax = excess_agi * rate

        return tax
