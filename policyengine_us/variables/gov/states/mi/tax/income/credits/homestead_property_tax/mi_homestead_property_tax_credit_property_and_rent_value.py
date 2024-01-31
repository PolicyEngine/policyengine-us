from policyengine_us.model_api import *


class mi_homestead_property_tax_credit_property_and_rent_value(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan homestead property tax credit property and rent value"
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
        ).gov.states.mi.tax.income.credits.homestead_property_tax

        property_value = add(tax_unit, period, ["assessed_property_value"])
        rent = add(tax_unit, period, ["rent"])

        applicable_rent = rent * p.rent_equivalization
        # Line 13
        return property_value + applicable_rent
