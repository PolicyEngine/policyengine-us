from policyengine_us.model_api import *


class nm_low_income_comprehensive_tax_rebate(Variable):
    value_type = float
    entity = TaxUnit
    label = "NM low income comprehensive tax rebate"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/34821a9573ca43e7b06dfad20f5183fd/1afc56af-ea90-4d48-82e5-1f9aeb43255a/PITbook2022.pdf#page=58",
        "https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/34821a9573ca43e7b06dfad20f5183fd/856ebf4b-3814-49dd-8631-ebe579d6a42b/Personal%20Income%20Tax.pdf#page=51"
    ) 
    # 7-2-7.6. 2021 INCOME TAX REBATE
    # SECTION II: LOW INCOME COMPREHENSIVE TAX REBATE
    defined_for = StateCode.NM

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.nm.tax.rebates.low_income_rebate

        agi = tax_unit("adjusted_gross_income", period)
        exemption_num = tax_unit("nm_number_of_exemption", period)

        rebate = ?

        filing_status = tax_unit("filing_status", period)
        statuses = filing_status.possible_values.SEPARATE

        if filing_status == statuses:
            rebate /= 2

        return rebate


