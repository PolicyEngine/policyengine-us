from policyengine_us.model_api import *


class ms_itemized_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Mississippi itemized exemption"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MS
    
    def formula(tax_unit, period, parameters):
        # compute itemized deduction maximum
        p = parameters(period).gov.irs.deductions
        itm_deds = [
            deduction
            for deduction in p.itemized_deductions
            if deduction not in ["salt_deduction"]
        ]
        itm_deds_less_salt = add(tax_unit, period, itm_deds)
        uncapped_property_taxes = add(tax_unit, period, ["real_estate_taxes"])
        itm_deds_max = itm_deds_less_salt + uncapped_property_taxes
        # calculate itemized deductions total amount
        p = parameters(period).gov.states.ms.tax.income.exemptions
        exempt_deds = add(
            tax_unit,
            period,
            ["medical_dental_expense", "taxes_paid" , "interest_paid" , "charitable_contribution" , "casualty_theft_loss" , "other_miscellaneous_deductions"],
        )
        net_deds = max_(0, ms_itm_deds - exempt_deds)
        net_deds_offset = p.deduction_fraction * net_deds
        agi = tax_unit("adjusted_gross_income", period)
        excess_agi = max_(0, agi - p.agi_threshold[filing_status])
        excess_agi_offset = p.excess_agi_fraction * excess_agi
        offset = min_(net_deds_offset, excess_agi_offset)
        return max_(0, ms_itm_deds - offset)

    
