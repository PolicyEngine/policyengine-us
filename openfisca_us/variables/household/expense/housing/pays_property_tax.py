from openfisca_us.model_api import *


class pays_property_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Flag for paying property tax"
    unit = USD
    definition_period = YEAR
    reference = "https://dor.mo.gov/forms/MO-PTS_2021.pdf"
    defined_for = StateCode.MO

    def formula(tax_unit, period, parameters):
        rent = add(tax_unit, period, ["rent"])
        #this is a naiive method of determing renter vs owner, unclear how it is determined in practice from the law,
        #refer to: https://revisor.mo.gov/main/OneSection.aspx?section=135.025&bid=6438 which states there should be regulations
        #dealing with similar cases, unable to find them on a quick search.
        return where(rent > 0, 1, 0)
