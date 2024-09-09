from policyengine_us.model_api import *


class ne_social_security_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Nebraska social security subtraction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NE

    def formula(tax_unit, period, parameters):
        fagi = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)
        p = parameters(period).gov.states.ne.tax.income.agi.subtractions
        oasdi_fraction = where(
            fagi <= p.social_security.threshold[filing_status],
            1.0,
            p.social_security.fraction,
        )
        taxable_oasdi = add(tax_unit, period, ["taxable_social_security"])
        return taxable_oasdi * oasdi_fraction
