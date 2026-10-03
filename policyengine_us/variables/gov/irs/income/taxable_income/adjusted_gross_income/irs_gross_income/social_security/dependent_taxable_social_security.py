from policyengine_us.model_api import *


class dependent_taxable_social_security(Variable):
    value_type = float
    entity = Person
    label = "Dependent's taxable Social Security"
    unit = USD
    documentation = """
    Social Security benefits that a dependent includes in gross income under
    IRC 86, figured on the dependent's own modified adjusted gross income and
    marital circumstances, independent of the claimant's filing status. A
    dependent does not file a joint return (IRC 152(b)(2)), so the joint
    amounts never apply. A dependent who lives with their spouse has zero
    base and adjusted base amounts under IRC 86(c)(1)(C) and (c)(2)(C), and
    every other dependent has the unmarried amounts.
    """
    definition_period = YEAR
    defined_for = "is_tax_unit_dependent"
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/86",
        "https://www.law.cornell.edu/uscode/text/26/152#b_2",
        # IRS Pub. 915 (2022): a dependent's benefits are added to the
        # dependent's own other income to determine their taxable part.
        "https://www.irs.gov/pub/irs-prior/p915--2022.pdf#page=5",
        # IRS Pub. 915 (2022), Worksheet 1, including the note to line 9.
        "https://www.irs.gov/pub/irs-prior/p915--2022.pdf#page=16",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.social_security.taxability
        gross_ss = max_(0, person("social_security", period))
        # IRC 86(b)(1): modified AGI plus one-half of the benefits.
        combined_income = (
            person("dependent_taxable_ss_magi", period)
            + p.combined_income_ss_fraction * gross_ss
        )
        lives_with_spouse = person("dependent_lives_with_spouse", period)
        base_amount = where(
            lives_with_spouse,
            p.threshold.base.separate_cohabitating,
            p.threshold.base.main["SINGLE"],
        )
        adjusted_base_amount = where(
            lives_with_spouse,
            p.threshold.adjusted_base.separate_cohabitating,
            p.threshold.adjusted_base.main["SINGLE"],
        )
        # IRC 86(a)(1): the lesser of half the benefits or half the excess of
        # combined income over the base amount.
        amount_under_paragraph_1 = min_(
            p.rate.base.benefit_cap * gross_ss,
            p.rate.base.excess * max_(0, combined_income - base_amount),
        )
        # IRC 86(a)(2)(A)(ii): the lesser of the paragraph (1) amount or half
        # the difference between the adjusted base and base amounts.
        bracket_amount = min_(
            amount_under_paragraph_1,
            p.rate.additional.bracket * (adjusted_base_amount - base_amount),
        )
        # IRC 86(a)(2): the lesser of 85 percent of the excess over the
        # adjusted base amount plus the bracket amount, or 85 percent of
        # the benefits.
        amount_over_adjusted_base = min_(
            p.rate.additional.excess * max_(0, combined_income - adjusted_base_amount)
            + bracket_amount,
            p.rate.additional.benefit_cap * gross_ss,
        )
        return select(
            [
                combined_income < base_amount,
                combined_income < adjusted_base_amount,
            ],
            [0, amount_under_paragraph_1],
            default=amount_over_adjusted_base,
        )
