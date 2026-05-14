from policyengine_us.model_api import *


class tn_elderly_property_tax_relief_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Tennessee elderly property tax relief"
    definition_period = YEAR
    reference = (
        "https://comptroller.tn.gov/office-functions/pa/property-taxes/property-tax-programs/tax-relief.html",
        "https://comptroller.tn.gov/content/dam/cot/pa/documents/tax-relief/TaxReliefBrochure.pdf",
        "https://comptroller.tn.gov/content/dam/cot/pa/documents/tax-relief/TCA%2067-5-701%20through%2067-5-704.pdf",
    )
    defined_for = StateCode.TN

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.tn.tax.property.elderly_property_tax_relief
        return (
            (tax_unit("greater_age_head_spouse", period) >= p.age_threshold)
            & (
                tax_unit("tn_elderly_property_tax_relief_income", period)
                <= p.income_limit
            )
            & (add(tax_unit, period, ["real_estate_taxes"]) > 0)
            & (add(tax_unit, period, ["assessed_property_value"]) > 0)
            & ~tax_unit("rents", period)
        )
