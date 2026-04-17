from policyengine_us.model_api import *


class ks_agi_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kansas AGI subtractions from federal AGI"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ksrevenue.gov/pdf/ip21.pdfhttps://www.ksrevenue.gov/pdf/ip22.pdf"
    )
    defined_for = StateCode.KS

    def formula(tax_unit, period, parameters):
        agi = tax_unit("adjusted_gross_income", period)
        taxable_oasdi = add(tax_unit, period, ["taxable_social_security"])
        p = parameters(period).gov.states.ks.tax.income.agi.subtractions
        oasdi_subtraction = where(agi <= p.oasdi.agi_limit, taxable_oasdi, 0)
        us_govt_interest = add(tax_unit, period, ["us_govt_interest"])
        return oasdi_subtraction + us_govt_interest
