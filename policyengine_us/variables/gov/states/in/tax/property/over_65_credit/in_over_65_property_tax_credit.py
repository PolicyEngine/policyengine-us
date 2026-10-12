from policyengine_us.model_api import *


class in_over_65_property_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Indiana Over 65 Property Tax Credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.in.gov/counties/monroe/Departments/auditor/over-65/",
        "https://www.in.gov/dlgf/files/2025-memos/250612-Cockerill-Memo-Legislation-Affecting-Deductions%2C-Exemptions%2C-and-Credits.pdf#page=2",
    )
    defined_for = "in_over_65_property_tax_credit_eligible"

    def formula(tax_unit, period, parameters):
        return min_(
            parameters(period).gov.states["in"].tax.property.over_65_credit.amount,
            add(tax_unit, period, ["real_estate_taxes"]),
        )
