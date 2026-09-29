from policyengine_us.model_api import *

# Montana "gross income" (MCA 15-30-2101(10)) starts from IRC 61 gross income
# but differs from the federal gross income sources in three places.
MT_GROSS_INCOME_SOURCE_OVERRIDES = {
    # Unemployment compensation is excluded from Montana gross income.
    "taxable_unemployment_compensation": [],
    # Only the IRC 86 taxable part of Social Security is gross income. It is
    # computed below on the dependent's own income.
    "taxable_social_security": [],
    # Gross income includes gains but not losses, so long-term and
    # short-term gains are each floored at zero instead of being netted.
    "capital_gains": ["long_term_capital_gains", "short_term_capital_gains"],
}


class mt_dependent_gross_income(Variable):
    value_type = float
    entity = Person
    label = "Montana gross income of a dependent for the dependent exemption"
    unit = USD
    definition_period = YEAR
    reference = (
        # MCA 15-30-2101(10) (2021): gross income is IRC 61 gross income
        # excluding unemployment compensation.
        "http://web.archive.org/web/20220127192023/http://leg.mt.gov/bills/mca/title_0150/chapter_0300/part_0210/section_0010/0150-0300-0210-0010.html",
        # MCA 15-30-2114(5)(a) (2021): the dependent gross income test.
        "http://web.archive.org/web/20220818141612/https://leg.mt.gov/bills/mca/title_0150/chapter_0300/part_0210/section_0140/0150-0300-0210-0140.html",
        # ARM 42.15.403 restates the test; its subsection numbers are not
        # verified because the rule text was not machine-readable.
        "https://rules.mt.gov/gateway/ruleno.asp?RN=42.15.403",
        # 2022 Form 2 instructions: "federal gross income, excluding
        # unemployment compensation".
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2022_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=7",
        # IRS Pub. 501 (2022): gross income includes gains but not losses, and
        # Social Security counts only when taxable.
        "https://www.irs.gov/pub/irs-prior/p501--2022.pdf#page=2",
        "https://www.irs.gov/pub/irs-prior/p501--2022.pdf#page=19",
        "https://www.law.cornell.edu/uscode/text/26/86",
    )
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        sources = parameters(period).gov.irs.gross_income.sources
        other_gross_income = 0
        for source in sources:
            components = MT_GROSS_INCOME_SOURCE_OVERRIDES.get(source, [source])
            for component in components:
                other_gross_income += max_(0, add(person, period, [component]))

        # Taxable Social Security under IRC 86, computed on the dependent's
        # own income with the single base amounts. Pub. 501: benefits are not
        # gross income unless "one-half of your social security benefits plus
        # your other gross income and any tax-exempt interest" exceeds the
        # base amount. Approximations: adjustments to income are ignored, and
        # the $0 base for a dependent who is married filing separately and
        # lives with their spouse is not modeled.
        p = parameters(period).gov.irs.social_security.taxability
        social_security = max_(0, person("social_security", period))
        # Unemployment compensation is federal gross income, so it counts
        # toward provisional income even though Montana excludes it from
        # gross income.
        unemployment_compensation = max_(0, person("unemployment_compensation", period))
        provisional_income = (
            other_gross_income
            + unemployment_compensation
            + person("tax_exempt_interest_income", period)
            + p.combined_income_ss_fraction * social_security
        )
        base_amount = p.threshold.base.main["SINGLE"]
        adjusted_base_amount = p.threshold.adjusted_base.main["SINGLE"]
        # IRC 86(a)(1): the lesser of half the benefits or half the excess of
        # provisional income over the base amount.
        amount_under_paragraph_1 = min_(
            p.rate.base.benefit_cap * social_security,
            p.rate.base.excess * max_(0, provisional_income - base_amount),
        )
        # IRC 86(a)(2): above the adjusted base amount.
        bracket_amount = min_(
            amount_under_paragraph_1,
            p.rate.additional.bracket * (adjusted_base_amount - base_amount),
        )
        amount_over_adjusted_base = min_(
            p.rate.additional.excess
            * max_(0, provisional_income - adjusted_base_amount)
            + bracket_amount,
            p.rate.additional.benefit_cap * social_security,
        )
        taxable_social_security = select(
            [
                provisional_income < base_amount,
                provisional_income < adjusted_base_amount,
            ],
            [0, amount_under_paragraph_1],
            default=amount_over_adjusted_base,
        )
        # Only dependents' own income is tested, as in dependent_gross_income.
        is_dependent = ~person("is_tax_unit_head_or_spouse", period)
        return is_dependent * (other_gross_income + taxable_social_security)
