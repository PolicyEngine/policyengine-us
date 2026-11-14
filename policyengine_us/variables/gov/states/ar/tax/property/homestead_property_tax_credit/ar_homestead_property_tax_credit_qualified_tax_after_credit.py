from policyengine_us.model_api import *


class ar_homestead_property_tax_credit_qualified_tax_after_credit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    unit = USD
    default_value = 0
    defined_for = "ar_homestead_property_tax_credit_inputs_available"
    label = "Arkansas qualified homestead tax after the property tax credit"
    reference = "https://www.arkleg.state.ar.us/Home/FTPDocument?path=%2FACTS%2F2005%2FPublic%2FACT1268.pdf#page=1"

    def formula_2025_01_01(tax_unit, period, parameters):
        qualified_property_taxes = tax_unit(
            "ar_homestead_property_tax_credit_qualified_property_taxes", period
        )
        credit = tax_unit("ar_homestead_property_tax_credit", period)
        return qualified_property_taxes - credit
