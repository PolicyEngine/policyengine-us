from policyengine_us.model_api import *


class nm_salt_add_back(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico salt addback"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/34821a9573ca43e7b06dfad20f5183fd/1afc56af-ea90-4d48-82e5-1f9aeb43255a/PITbook2022.pdf#page=28",
        "https://law.justia.com/codes/new-mexico/chapter-7/article-2/section-7-2-2/",
        "https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/34821a9573ca43e7b06dfad20f5183fd/1afc56af-ea90-4d48-82e5-1f9aeb43255a/PITbook2022.pdf#page=28",
    )
    defined_for = StateCode.NM

    def formula(tax_unit, period, parameters):
        itemizes = tax_unit("tax_unit_itemizes", period)
        filing_status = tax_unit("filing_status", period)
        p = parameters(period).gov.irs.deductions

        # tax/income, federal Schedule A, line 5a. 1
        salt_sales_or_income = tax_unit(
            "state_and_local_sales_or_income_tax", period
        )
        # state_and_local_tax, line 5d. 2
        total_salt = (
            add(tax_unit, period, ["real_estate_taxes"]) + salt_sales_or_income
        )
        # ratio = round(salt_sales_or_income[0] / total_salt[0], 4)
        # ratio. 3
        salt_ratio = np.zeros_like(total_salt)
        mask = total_salt != 0
        salt_ratio[mask] = salt_sales_or_income[mask] / total_salt[mask]

        # line 5e. 4
        salt_cap = p.itemized.salt_and_real_estate.cap[filing_status]
        salt_claimed = min_(salt_cap, total_salt)

        # 5 = salt_claimed * salt_ratio
        # 6 = min(5, 4)
        salt = min_(salt_claimed * salt_ratio, salt_claimed)

        standard_deduction = tax_unit("standard_deduction", period)
        itm_deds_less_salt = tax_unit("itemized_deductions_less_salt", period)
        us_itemized_deductions = itm_deds_less_salt + salt_claimed
        item_deds = max_(us_itemized_deductions - standard_deduction, 0)

        nm_item = min_(salt, item_deds)
        return where(itemizes, nm_item, 0)
