from policyengine_us.model_api import *


class nm_low_income_comprehensive_tax_rebate(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico low income comprehensive tax rebate"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/34821a9573ca43e7b06dfad20f5183fd/1afc56af-ea90-4d48-82e5-1f9aeb43255a/PITbook2022.pdf#page=58",
        "https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/34821a9573ca43e7b06dfad20f5183fd/1afc56af-ea90-4d48-82e5-1f9aeb43255a/PITbook2022.pdf#page=70",
        "https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/34821a9573ca43e7b06dfad20f5183fd/856ebf4b-3814-49dd-8631-ebe579d6a42b/Personal%20Income%20Tax.pdf#page=67",
        "https://casetext.com/statute/new-mexico-statutes-1978/chapter-7-taxation/article-2-income-tax-general-provisions/section-7-2-14-low-income-comprehensive-tax-rebate?sort=relevance&type=regulation&tab=keyword&jxs=&resultsNav=false",
    )
    # 7-2-7.6. 2021 INCOME TAX REBATE
    # SECTION II: LOW INCOME COMPREHENSIVE TAX REBATE
    defined_for = StateCode.NM

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nm.tax.income.rebates.low_income

        agi = tax_unit("nm_modified_gross_income", period)
        exemptions = tax_unit("exemptions", period)

        rebate = select(
            [
                exemptions == 1,
                exemptions == 2,
                exemptions == 3,
                exemptions == 4,
                exemptions == 5,
                exemptions >= 6,
            ],
            [
                p.amount.one_exemption.calc(agi),
                p.amount.two_exemptions.calc(agi),
                p.amount.three_exemptions.calc(agi),
                p.amount.four_exemptions.calc(agi),
                p.amount.five_exemptions.calc(agi),
                p.amount.six_exemptions.calc(agi),
            ],
        )

        filing_status = tax_unit("filing_status", period)
        divisor = where(
            filing_status == filing_status.possible_values.SEPARATE,
            p.divisor,
            1,
        )
        return rebate / divisor
