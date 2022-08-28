from openfisca_us.model_api import *

class mo_property_tax_credit_rent_or_own(Variable):
    value_type = float
    entity = TaxUnit
    label = "Renter or owner for MO Property Tax Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://dor.mo.gov/forms/MO-PTS_2021.pdf"
    defined_for = StateCode.MO

    def formula(tax_unit, period, parameters):
        rent = add(tax_unit, period, ["rent"])
        property_tax = tax_unit.household("real_estate_taxes", period)      
        return where(property_tax > rent, 'OWNER', 'RENTER')
