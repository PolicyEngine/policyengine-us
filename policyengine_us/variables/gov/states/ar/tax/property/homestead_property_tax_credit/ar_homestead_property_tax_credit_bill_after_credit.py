from policyengine_us.model_api import *


class ar_homestead_property_tax_credit_bill_after_credit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    unit = USD
    default_value = 0
    defined_for = "ar_homestead_property_tax_credit_bill_available"
    label = "Arkansas parcel's complete bill after the homestead property tax credit"
    reference = "https://www.arkleg.state.ar.us/Home/FTPDocument?path=%2FACTS%2F2005%2FPublic%2FACT1268.pdf#page=1"

    def formula_2025_01_01(tax_unit, period, parameters):
        bill_before_credit = tax_unit(
            "ar_homestead_property_tax_credit_bill_before_credit", period
        )
        credit = tax_unit("ar_homestead_property_tax_credit", period)
        return bill_before_credit - credit
