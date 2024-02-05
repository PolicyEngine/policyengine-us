from policyengine_us.model_api import *


class sc_state_tax_addback(Variable):
    value_type = float
    entity = TaxUnit
    label = "South Carolina State Tax addback"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.sc.gov/forms-site/Forms/SC1040_2022.pdf#page=2",
        "https://dor.sc.gov/forms-site/Forms/SC1040inst_2022.pdf#page=2",
        "https://www.scstatehouse.gov/code/t12c006.php",  # SECTION 12-6-1130 (2)
    )
    defined_for = StateCode.SC

    def formula(tax_unit, period, parameters):
        p_us = parameters(period).gov.irs.deductions

        us_itemizing = tax_unit("tax_unit_itemizes", period)
        standard_deduction = tax_unit("standard_deduction", period)
        filing_status = tax_unit("filing_status", period)
        eligible = filing_status != filing_status.possible_values.SEPARATE
        # line 1
        federal_itemized_deduction = (
            tax_unit("itemized_taxable_income_deductions", period)
            * us_itemizing
        )
        # line 2
        federal_standard_deduction = standard_deduction * eligible
        # line 3
        less_itm_amount = max_(
            0, federal_itemized_deduction - federal_standard_deduction
        )
        # line 4
        salt = tax_unit("state_and_local_sales_or_income_tax", period)
        # line 5
        real_estate_and_property_taxes = add(
            tax_unit, period, ["real_estate_taxes"]
        )
        less_income_amount = max_(
            0,
            p_us.itemized.salt_and_real_estate.cap[filing_status]
            - real_estate_and_property_taxes,
        )
        # compare line 3,4,5. get the minimum
        salt_or_income = min_(salt, less_income_amount)
        return min_(salt_or_income, less_itm_amount)
