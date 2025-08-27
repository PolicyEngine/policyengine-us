from policyengine_us.model_api import *


class md_poverty_line_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD Poverty Line Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://law.justia.com/codes/maryland/2021/tax-general/title-10/subtitle-7/section-10-709/"
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        # Earlier portions of the law define eligibility.
        eligible = tax_unit("is_eligible_md_poverty_line_credit", period)
        # (c)    Except as provided in subsection (e) of this section, the
        # credit allowed against the State income tax under subsection (b)(1)
        # of this section equals the lesser of:
        # (1) the State income tax determined after subtracting the credit
        # allowed under § 10–704(b)(1) of this subtitle; or
        income_tax_before_credits = tax_unit(
            "md_income_tax_before_credits", period
        )
        md_married_or_has_child_non_refundable_eitc = tax_unit(
            "md_married_or_has_child_non_refundable_eitc", period
        )
        tax_after_non_refundable_eitc = (
            income_tax_before_credits
            - md_married_or_has_child_non_refundable_eitc
        )
        # (2)    an amount equal to 5% of the eligible low income taxpayer’s
        # earned income, as defined under § 32(c)(2) of the Internal Revenue
        # Code.
        p = parameters(period).gov.states.md.tax.income.credits.poverty_line
        earnings = tax_unit("tax_unit_earned_income", period)
        earnings_portion = earnings * p.earned_income_share
        amount_if_eligible = min_(
            tax_after_non_refundable_eitc, earnings_portion
        )
        return amount_if_eligible * eligible
