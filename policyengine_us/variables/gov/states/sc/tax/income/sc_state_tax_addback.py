from policyengine_us.model_api import *


class sc_state_tax_addback(Variable):
    value_type = float
    entity = TaxUnit
    label = "South Carolina State Tax addback"
    unit = USD
    definition_period = YEAR
    reference = "https://dor.sc.gov/forms-site/Forms/SC1040_2022.pdf"
    defined_for = StateCode.SC

    def formula(tax_unit, period, parameters):
        p_us = parameters(period).gov.irs.deductions
        itm_deds = [deduction for deduction in p_us.itemized_deductions]
        deds_if_not_itm = [
            deduction for deduction in p_us.deductions_if_not_itemizing
        ]
        filing_status = tax_unit("filing_status", period)
        eligible = filing_status != filing_status.possible_values.SEPARATE
        # line 1
        federal_itemized_deduction = add(tax_unit, period, itm_deds)
        # line 2
        federal_deduction_if_not_itemizing = (
            add(tax_unit, period, deds_if_not_itm) * eligible
        )
        # line 3
        less_itm_amount = max_(
            0, federal_itemized_deduction - federal_deduction_if_not_itemizing
        )
        # line 4
        salt = tax_unit("state_and_local_sales_or_income_tax", period)
        # line 5
        capped_property_taxes = min_(
            add(tax_unit, period, ["real_estate_taxes"]),
            p_us.itemized.salt_and_real_estate.cap[filing_status],
        )
        less_income_amount = (
            p_us.itemized.salt_and_real_estate.cap[filing_status]
            - capped_property_taxes
        )
        # compare line 3,4,5. get the minimum
        return min(less_itm_amount, salt, less_income_amount)
