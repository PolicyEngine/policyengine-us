from policyengine_us.model_api import *


class pays_property_tax_or_rent(Variable):
    value_type = float
    entity = TaxUnit
    label = "Household pays rent or property tax"
    unit = USD
    definition_period = YEAR
    reference = "https://dor.mo.gov/forms/MO-PTS_2021.pdf"

    def formula(tax_unit, period, parameters):
        return add(tax_unit, period, ["rent", "real_estate_taxes"]) > 0
