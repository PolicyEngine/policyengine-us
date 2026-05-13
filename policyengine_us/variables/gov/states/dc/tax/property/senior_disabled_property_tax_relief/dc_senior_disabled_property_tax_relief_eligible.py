from policyengine_us.model_api import *


class dc_senior_disabled_property_tax_relief_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the DC senior disabled property tax relief"
    definition_period = YEAR
    reference = (
        "https://otr.cfo.dc.gov/page/"
        "real-property-tax-reliefs-credits-and-deductions",
        "https://code.dccouncil.gov/us/dc/council/code/sections/47-863",
    )
    defined_for = StateCode.DC

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.dc.tax.property.senior_disabled_property_tax_relief
        age_eligible = tax_unit("greater_age_head_spouse", period) >= p.age_threshold
        disabled = tax_unit("disabled_tax_unit_head_or_spouse", period)
        income = tax_unit.spm_unit(
            "dc_senior_disabled_property_tax_relief_income", period
        )
        income_eligible = income < p.income_limit
        pays_property_taxes = add(tax_unit, period, ["real_estate_taxes"]) > 0
        is_renter = tax_unit("rents", period)
        return (
            (age_eligible | disabled)
            & income_eligible
            & pays_property_taxes
            & ~is_renter
        )
