from policyengine_us.model_api import *


class nm_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/34821a9573ca43e7b06dfad20f5183fd/1afc56af-ea90-4d48-82e5-1f9aeb43255a/PITbook2022.pdf#page=28"
    )
    defined_for = StateCode.NM

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)

        # tax/income, federal Schedule A, line 5a.
        slat_sales_or_income = tax_unit(
            "state_and_local_sales_or_income_tax", period
        )
        # state_and_local_tax, line 5d
        total_salt = tax_unit("real_estate_taxes", period) + slat_sales_or_income
        ratio = round(slat_sales_or_income / total_salt, 4)
        
        # line 5e
        # salt_claimed = tax_unit("salt_deduction", period)
        salt = salt_claimed * min(ratio, 1)
        
        standard_deduction = tax_unit("standard_deduction", period)
        p = parameters(period).gov.irs.deductions
        itm_deds = [
            deduction
            for deduction in p.itemized_deductions
        ]
        us_itmemized_deductions = add(tax_unit, period, itm_deds)
        item_deds = max(us_itmemized_deductions - standard_deduction, 0)
        return min(salt, item_deds)

        # 
        # adjustment_base_amount = parameters(
            # period
        # ).gov.irs.deductions.itemized.salt_and_real_estate.cap[filing_status]

        

