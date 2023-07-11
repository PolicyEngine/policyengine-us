from policyengine_us.model_api import *


class nm_property_tax_rebate(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico property tax rebate"
    unit = USD
    definition_period = YEAR
    reference = "https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/34821a9573ca43e7b06dfad20f5183fd/1afc56af-ea90-4d48-82e5-1f9aeb43255a/PITbook2022.pdf"
    default_value = 0

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nm.tax.income.rebates
        rent_paid = tax_unit( "rent", period)
        rebate_rate = tax_unit("rate", period)

        return rent_paid * rebate_rate
