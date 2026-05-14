from policyengine_us.model_api import *


class tn_elderly_property_tax_relief(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tennessee elderly property tax relief"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://comptroller.tn.gov/office-functions/pa/property-taxes/property-tax-programs/tax-relief.html",
        "https://comptroller.tn.gov/content/dam/cot/pa/documents/tax-relief/TaxReliefBrochure.pdf",
        "https://comptroller.tn.gov/content/dam/cot/pa/documents/tax-relief/TCA%2067-5-701%20through%2067-5-704.pdf",
    )
    defined_for = "tn_elderly_property_tax_relief_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.tn.tax.property.elderly_property_tax_relief
        assessed_property_value = add(tax_unit, period, ["assessed_property_value"])
        capped_assessed_property_value = min_(
            assessed_property_value,
            p.property_value_cap * p.assessment_rate,
        )
        return (
            add(tax_unit, period, ["real_estate_taxes"])
            * capped_assessed_property_value
            / assessed_property_value
        )
