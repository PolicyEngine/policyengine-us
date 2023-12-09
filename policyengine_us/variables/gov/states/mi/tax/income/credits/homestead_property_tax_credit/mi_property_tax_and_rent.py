from policyengine_us.model_api import *


class mi_property_tax_and_rent(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan property tax and rent"
    unit = USD
    definition_period = YEAR
    reference = (
        "http://legislature.mi.gov/doc.aspx?mcl-206-508",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/MI-1040CR.pdf#page=1",
    )
    defined_for = StateCode.MI

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mi.tax.income.credits.homestead_property_tax_credit.rate

        property_value = add(tax_unit, period, ["assessed_property_value"])
        rents = add(tax_unit, period, ["rent"])

        return property_value + rents * p.rent  # Line 13
