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
        # tax/income
        slat_sales_or_income = tax_unit(
            "state_and_local_sales_or_income_tax", period
        )
        # state_and_local_tax
        total_salt = tax_unit("real_estate_taxes", period) + slat_sales_or_income
        salt_claimed = tax_unit("salt_deduction", period)
        ratio = round(slat_sales_or_income / total_salt)

        filing_status = tax_unit("filing_status", period)
        adjustment_base_amount = parameters(
            period
        ).gov.irs.deductions.itemized.salt_and_real_estate.cap[filing_status]

        standard_deduction = tax_unit("standard_deduction", period)

