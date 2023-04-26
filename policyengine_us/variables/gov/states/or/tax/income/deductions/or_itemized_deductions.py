from policyengine_us.model_api import *


class or_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "OR itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = "https://www.oregonlegislature.gov/bills_laws/ors/ors316.html"  # 316.695 (1)(d)
    defined_for = StateCode.OR

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.deductions
        itm_deds = [
            deduction
            for deduction in p.itemized_deductions
            if deduction not in ["salt_deduction"]
        ]
        or_itemized_deductions_less_salt = add(tax_unit, period, itm_deds)
        property_taxes = add(tax_unit, period, ["real_estate_taxes"])
        salt = p.itemized.salt_and_real_estate
        cap = salt.cap[tax_unit("filing_status", period)]
        capped_property_taxes = min_(property_taxes, cap)
        return or_itemized_deductions_less_salt + capped_property_taxes
