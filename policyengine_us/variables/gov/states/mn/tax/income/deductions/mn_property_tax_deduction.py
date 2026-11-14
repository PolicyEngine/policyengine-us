from policyengine_us.model_api import *


class mn_property_tax_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota property tax deduction"
    unit = USD
    definition_period = YEAR
    documentation = "Real estate and personal property taxes allowable for Minnesota itemized deductions."
    reference = "https://www.revisor.mn.gov/statutes/cite/290.0122#stat.290.0122.3"
    defined_for = StateCode.MN

    def formula(tax_unit, period, parameters):
        return tax_unit("capped_property_taxes", period)

    def formula_2025(tax_unit, period, parameters):
        property_taxes = add(
            tax_unit, period, ["real_estate_taxes", "mn_personal_property_taxes"]
        )
        p = parameters(
            period
        ).gov.states.mn.tax.income.deductions.itemized.property_taxes
        filing_status = tax_unit("filing_status", period)
        return min_(property_taxes, p.cap[filing_status])
