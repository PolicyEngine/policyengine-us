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
        #this is a naiive method of determing renter vs owner, unclear how it is determined in practice from the law,
        #refer to: https://revisor.mo.gov/main/OneSection.aspx?section=135.025&bid=6438 which states there should be regulations
        #dealing with similar cases, unable to find them on a quick search.
        return where(property_tax > rent, 'OWNER', 'RENTER')
