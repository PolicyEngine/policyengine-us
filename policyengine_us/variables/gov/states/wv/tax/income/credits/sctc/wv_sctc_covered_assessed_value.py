from policyengine_us.model_api import *


class wv_sctc_covered_assessed_value(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    quantity_type = STOCK
    unit = USD
    label = "West Virginia SCTC covered taxable assessed value"
    reference = "https://code.wvlegislature.gov/11-21-21/"
    defined_for = "wv_sctc_eligible"

    def formula_2025_01_01(tax_unit, period, parameters):
        payment_known = tax_unit("wv_sctc_payment_inputs_available", period)
        value = tax_unit("wv_sctc_taxable_assessed_value", period)
        p = parameters(period).gov.states.wv.tax.income.credits.sctc
        return where(payment_known, min_(value, max_(p.max_amount, 0)), 0)
