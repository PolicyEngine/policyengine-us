from policyengine_us.model_api import *


class dc_senior_disabled_property_tax_relief(Variable):
    """Bill reduction using an explicit, once-only pre-relief tax base from 2025.

    This is not an additional cash refund on an already-reduced property-tax bill.
    """

    value_type = float
    entity = TaxUnit
    label = "DC senior disabled property tax relief"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://otr.cfo.dc.gov/page/real-property-tax-reliefs-credits-and-deductions",
        "https://code.dccouncil.gov/us/dc/council/code/sections/47-863",
    )
    defined_for = "dc_senior_disabled_property_tax_relief_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.dc.tax.property.senior_disabled_property_tax_relief
        return add(tax_unit, period, ["real_estate_taxes"]) * p.rate

    def formula_2025(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.dc.tax.property.senior_disabled_property_tax_relief
        tax = tax_unit("dc_senior_disabled_property_tax_relief_pre_relief_tax", period)
        return max_(tax, 0) * p.rate
