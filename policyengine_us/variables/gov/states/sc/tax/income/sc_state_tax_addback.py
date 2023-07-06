from policyengine_us.model_api import *


class sc_state_tax_addback(Variable):
    value_type = float
    entity = TaxUnit
    label = "South Carolinz State Tax addback"
    unit = USD
    definition_period = YEAR
    reference = ""
    defined_for = StateCode.SC

    def formula(tax_unit, period, parameters):
        p_us = parameters(period).gov.irs.deductions
        itm_deds = [
            deduction
            for deduction in p_us.itemized_deductions
            #if deduction not in ["salt_deduction"]
        ]

        deds_if_not_itm = [
            deduction
            for deduction in p_us.deductions_if_not_itemizming
            #if deduction not in ["salt_deduction"]
        ]
        filing_status = tax_unit("filing_status", period)

        # line 1 
        federal_itemized_deduction = add(tax_unit, period, itm_deds)
        # line 2 
        federal_deduction_if_not_itemizming = add(tax_unit, period, deds_if_not_itm)
        # line 3
        max_(0,federal_deduction_if_not_itemizming - federal_itemized_deduction)

        # line 4 
        us_itm_deds_less_salt = add(tax_unit, period, itm_deds)
        capped_property_taxes = min_(
            add(tax_unit, period, ["real_estate_taxes"]),
            p.itemized.salt_and_real_estate.cap[filing_status],
        )
        p_sc = parameters(period).gov.states.sc.tax.income

        # line 5
        # compare linee 3,4,5. get the minimum 
        