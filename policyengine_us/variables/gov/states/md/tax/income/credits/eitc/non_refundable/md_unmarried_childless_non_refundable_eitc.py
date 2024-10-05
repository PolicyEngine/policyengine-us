from policyengine_us.model_api import *


class md_unmarried_childless_non_refundable_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maryland unmarried childless non-refundable EITC"
    unit = USD
    definition_period = YEAR
    reference = "https://casetext.com/statute/code-of-maryland/article-tax-general/title-10-income-tax/subtitle-7-income-tax-credits/section-10-704-effective-until-6302023-for-earned-income"  # (c)(3)
    defined_for = "md_qualifies_for_unmarried_childless_eitc"

    def formula(tax_unit, period, parameters):
        # individuals can claim the state eitc even they do not meet the minimum age requirement under the federal credit
        federal_eitc_without_age_minimum = tax_unit(
            "federal_eitc_without_age_minimum", period
        )
        p = parameters(
            period
        ).gov.states.md.tax.income.credits.eitc.non_refundable.unmarried_childless
        match = p.match * federal_eitc_without_age_minimum
        cap = p.max_amount
        return min_(match, cap)
