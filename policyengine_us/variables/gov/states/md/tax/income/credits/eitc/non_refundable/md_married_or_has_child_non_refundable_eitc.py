from policyengine_us.model_api import *


class md_married_or_has_child_non_refundable_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maryland non-refundable EITC for filers who are married or have qualifying child"
    unit = USD
    definition_period = YEAR
    reference = "https://casetext.com/statute/code-of-maryland/article-tax-general/title-10-income-tax/subtitle-7-income-tax-credits/section-10-704-effective-until-6302023-for-earned-income"  # (c)(1)
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        federal_eitc = tax_unit("eitc", period)

        p = parameters(
            period
        ).gov.states.md.tax.income.credits.eitc.non_refundable.married_or_has_child
        # Limited to filers who are married or have child
        married_or_has_child = ~tax_unit(
            "md_qualifies_for_unmarried_childless_eitc", period
        )
        amount = federal_eitc * p.match
        return married_or_has_child * amount
