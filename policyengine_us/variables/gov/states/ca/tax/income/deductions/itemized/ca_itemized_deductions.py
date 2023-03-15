from policyengine_us.model_api import *


class ca_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "California itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ftb.ca.gov/forms/2021/2021-540.pdf"
        "https://www.ftb.ca.gov/forms/2022/2022-540.pdf"
    )
    defined_for = StateCode.CA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.deductions
        itm_deds = [
            deduction
            for deduction in p.itemized_deductions
            if deduction not in ["salt_deduction"]
        ]
        itm_deds_less_salt = add(tax_unit, period, itm_deds)
        property_taxes = add(tax_unit, period, ["real_estate_taxes"])
        salt = p.itemized.salt_and_real_estate
        cap = salt.cap[tax_unit("filing_status", period)]
        capped_property_taxes = min_(property_taxes, cap)
        return itm_deds_less_salt + capped_property_taxes
