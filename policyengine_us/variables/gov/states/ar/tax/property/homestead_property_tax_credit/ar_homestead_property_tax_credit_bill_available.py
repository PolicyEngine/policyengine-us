from policyengine_us.model_api import *


class ar_homestead_property_tax_credit_bill_available(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    default_value = False
    defined_for = "ar_homestead_property_tax_credit_inputs_available"
    label = "The complete Arkansas parcel bill is available for the homestead credit"
    reference = "https://www.arkleg.state.ar.us/Home/FTPDocument?path=%2FACTS%2F2005%2FPublic%2FACT1268.pdf#page=1"

    def formula_2025_01_01(tax_unit, period, parameters):
        bill_before_credit = tax_unit(
            "ar_homestead_property_tax_credit_bill_before_credit", period
        )
        qualified_property_taxes = tax_unit(
            "ar_homestead_property_tax_credit_qualified_property_taxes", period
        )
        return bill_before_credit >= qualified_property_taxes
