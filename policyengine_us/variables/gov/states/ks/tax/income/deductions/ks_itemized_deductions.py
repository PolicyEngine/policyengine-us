from policyengine_us.model_api import *


class ks_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "KS itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ksrevenue.gov/pdf/ip21.pdf"
        "https://www.ksrevenue.gov/pdf/ip22.pdf"
    )
    defined_for = StateCode.KS

    def formula(tax_unit, period, parameters):
        # compute itemized deduction maximum
        p = parameters(period).gov.irs.deductions
        itm_deds = [
            deduction
            for deduction in p.itemized_deductions
            if deduction not in ["salt_deduction"]
        ]
        federal_itm_deds_less_salt = add(tax_unit, period, itm_deds)
        uncapped_property_taxes = add(tax_unit, period, ["real_estate_taxes"])
        return federal_itm_deds_less_salt + uncapped_property_taxes
