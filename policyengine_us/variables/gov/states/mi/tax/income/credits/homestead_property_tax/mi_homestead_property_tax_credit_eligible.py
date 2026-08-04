from policyengine_us.model_api import *


class mi_homestead_property_tax_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Michigan homestead property tax credit"
    definition_period = YEAR
    reference = (
        "http://legislature.mi.gov/doc.aspx?mcl-206-508",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/MI-1040CR.pdf#page=1",
        "https://www.legislature.mi.gov/Publications/TaxpayerGuide.pdf#page=16",
    )
    defined_for = StateCode.MI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mi.tax.income.credits.homestead_property_tax
        property_value_eligible = (
            add(tax_unit, period, ["assessed_property_value"]) <= p.property_value_limit
        )
        household_resources_eligible = (
            tax_unit("mi_household_resources", period) <= p.household_resources_limit
        )
        return property_value_eligible & household_resources_eligible
