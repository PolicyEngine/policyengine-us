from openfisca_us.model_api import *


class md_single_childless_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD single childless EITC"
    unit = USD
    definition_period = YEAR
    reference = "https://casetext.com/statute/code-of-maryland/article-tax-general/title-10-income-tax/subtitle-7-income-tax-credits/section-10-704-effective-until-6302023-for-earned-income"  # (c)(3)

    def formula(tax_unit, period, parameters):
        single_childless = tax_unit(
            "md_qualifies_for_single_childless_eitc", period
        )
        in_md = tax_unit.household("state_code_str", period) == "MD"
        eligible = single_childless & in_md
        federal_eitc_without_age_minimum = tax_unit(
            "federal_eitc_without_age_minimum", period
        )
        p = parameters(period).gov.states.md.tax.income.credits.eitc.childless
        match = p.percent_match * federal_eitc_without_age_minimum
        cap = p.max_amount
        return eligible * min_(match, cap)
