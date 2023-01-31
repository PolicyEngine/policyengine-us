from policyengine_us.model_api import *


class md_non_single_childless_non_refundable_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = (
        "MD non-refundable EITC for filers who are not single and childless"
    )
    unit = USD
    definition_period = YEAR
    reference = "https://casetext.com/statute/code-of-maryland/article-tax-general/title-10-income-tax/subtitle-7-income-tax-credits/section-10-704-effective-until-6302023-for-earned-income"  # (c)(1)
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        federal_eitc = tax_unit("eitc", period)
        p = parameters(period).gov.states.md.tax.income.credits.eitc
        tax_before_credits = tax_unit("md_income_tax_before_credits", period)
        # Limited to filers who are not single and childless.
        single_childless = tax_unit(
            "md_qualifies_for_single_childless_eitc", period
        )
        eligible = ~single_childless
        uncapped = p.non_refundable_match * federal_eitc
        amount = eligible * min_(tax_before_credits, uncapped)
        has_children = add(tax_unit, period, ["is_child"]) > 0
        mca = parameters(period).gov.contrib.maryland_child_alliance
        if mca.abolish_non_refundable_child_eitc:
            return amount * ~has_children
        else:
            return amount
