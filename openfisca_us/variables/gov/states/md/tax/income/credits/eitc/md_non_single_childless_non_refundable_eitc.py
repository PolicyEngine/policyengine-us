from openfisca_us.model_api import *


class md_non_single_childless_non_refundable_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = (
        "MD non-refundable EITC for filers who are not single and childless"
    )
    unit = USD
    definition_period = YEAR
    reference = "https://casetext.com/statute/code-of-maryland/article-tax-general/title-10-income-tax/subtitle-7-income-tax-credits/section-10-704-effective-until-6302023-for-earned-income"  # (c)(1)

    def formula(tax_unit, period, parameters):
        federal_eitc = tax_unit("eitc", period)
        p = parameters(period).gov.states.md.tax.income.credits.eitc
        tax_before_credits = tax_unit("md_income_tax_before_credits", period)
        # Limited to filers who are not single and childless.
        single_childless = tax_unit(
            "md_qualifies_for_single_childless_eitc", period
        )
        in_md = tax_unit.household("state_code_str", period) == "MD"
        eligible = ~single_childless & in_md
        uncapped = p.non_refundable_match * federal_eitc
        return eligible * min_(tax_before_credits, uncapped)
