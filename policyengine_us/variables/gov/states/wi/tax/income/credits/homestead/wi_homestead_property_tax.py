from policyengine_us.model_api import *


class wi_homestead_property_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin homestead credit property tax amount"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.wi.gov/TaxForms2021/2021-ScheduleH.pdf#page=2"
        "https://www.revenue.wi.gov/TaxForms2022/2022-ScheduleH.pdf#page=2"
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        ptax_owner = add(tax_unit, period, ["real_estate_taxes"])
        rent = add(tax_unit, period, ["rent"])
        p = parameters(period).gov.states.wi.tax.income.credits
        ptax_renter = rent * p.homestead.property_tax.rent_ratio
        return ptax_owner + ptax_renter
