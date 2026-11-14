from policyengine_us.model_api import *


class wv_sctc_payment_inputs_available(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "West Virginia SCTC payment inputs are available and valid"
    reference = "https://code.wvlegislature.gov/11-21-21/"
    defined_for = StateCode.WV

    def formula_2025_01_01(tax_unit, period, parameters):
        confirmed = tax_unit("wv_sctc_payment_facts_available", period)
        value = tax_unit("wv_sctc_taxable_assessed_value", period)
        paid = tax_unit("wv_sctc_qualified_property_taxes_paid", period)
        return (
            confirmed
            & np.isfinite(value)
            & np.isfinite(paid)
            & (value >= 0)
            & (paid >= 0)
            & ((value > 0) | (paid == 0))
        )
