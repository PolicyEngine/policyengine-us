from policyengine_us.model_api import *


class wv_sctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "West Virginia senior citizens tax credit"
    defined_for = "wv_sctc_eligible"
    unit = USD
    definition_period = YEAR
    reference = "https://code.wvlegislature.gov/11-21-21/"

    def formula(tax_unit, period, parameters):
        wv_taxable_property_value = tax_unit(
            "wv_taxable_property_value", period
        )
        p = parameters(period).gov.states.wv.tax.income.credits.sctc

        return min_(wv_taxable_property_value, p.max_amount)
