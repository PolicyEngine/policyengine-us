from policyengine_us.model_api import *


class ar_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "AR itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = 
    defined_for = StateCode.AR

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ar.tax.income.deductions.itemized

        # itm_deds = [
        #     deduction
        #     for deduction in p.itemized_deductions
        #     if deduction not in ["salt_deduction"]
        # ]
        # or_itemized_deductions_less_salt = add(tax_unit, period, itm_deds)
        # property_taxes = add(tax_unit, period, ["real_estate_taxes"])
        # salt = p.itemized.salt_and_real_estate
        # cap = salt.cap[tax_unit("filing_status", period)]
        # capped_property_taxes = min_(property_taxes, cap)
        # return or_itemized_deductions_less_salt + capped_property_taxes
        return 0