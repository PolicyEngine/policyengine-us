from openfisca_us.model_api import *


class md_non_single_childless_refundable_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD refundable EITC for filers who are not single and childless"
    unit = USD
    definition_period = YEAR
    reference = "https://casetext.com/statute/code-of-maryland/article-tax-general/title-10-income-tax/subtitle-7-income-tax-credits/section-10-704-effective-until-6302023-for-earned-income"
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        single_childless = tax_unit(
            "md_qualifies_for_single_childless_eitc", period
        )
        in_md = tax_unit.household("state_code_str", period) == "MD"
        # Must have zeroed out MD tax liability with non-refundable EITC.
        md_tax_before_credits = tax_unit(
            "md_income_tax_before_credits", period
        )
        md_non_single_childless_non_refundable_eitc = tax_unit(
            "md_non_single_childless_non_refundable_eitc", period
        )
        md_tax_equals_non_refundable_eitc = (
            md_tax_before_credits
            == md_non_single_childless_non_refundable_eitc
        )
        eligible = (
            in_md & ~single_childless & md_tax_equals_non_refundable_eitc
        )
        federal_eitc_without_age_minimum = tax_unit(
            "federal_eitc_without_age_minimum", period
        )
        p = parameters(period).gov.states.md.tax.income.credits.eitc
        matched_eitc = p.refundable_match * federal_eitc_without_age_minimum
        return eligible * max_(0, matched_eitc - md_tax_before_credits)
