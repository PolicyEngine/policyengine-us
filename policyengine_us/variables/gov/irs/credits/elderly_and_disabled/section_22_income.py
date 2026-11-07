from policyengine_us.model_api import *


class section_22_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Section 22 income"
    unit = USD
    documentation = "Income upon which the elderly or disabled credit is applied"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/22#c",
        "https://www.law.cornell.edu/uscode/text/26/22#e_1",
        # 2024 Instructions for Schedule R, lines 13a and 13b.
        "https://www.irs.gov/pub/irs-prior/i1040sr--2024.pdf#page=5",
    )

    def formula(tax_unit, period, parameters):
        elderly_disabled = parameters(period).gov.irs.credits.elderly_or_disabled
        # Calculate initial amount
        filing_status = tax_unit("filing_status", period)
        person = tax_unit.members
        num_qualifying_individuals = tax_unit.sum(
            person("qualifies_for_elderly_or_disabled_credit", period)
        )
        separate = filing_status == filing_status.possible_values.SEPARATE
        # Section 22(c)(2)(A)(iii) sets a separate filer's initial amount,
        # so the separate-return condition comes first: select takes the
        # first true condition. It tests n >= 1, not n == 1, because
        # qualifies_for_elderly_or_disabled_credit is not limited to the
        # head and spouse: a separate filer with a qualifying dependent
        # counts two, and would otherwise fall through to $7,500.
        initial_amount = select(
            [
                separate & (num_qualifying_individuals >= 1),
                num_qualifying_individuals == 1,
                num_qualifying_individuals == 2,
            ],
            [
                elderly_disabled.amount.separate,
                elderly_disabled.amount.one_qualified,
                elderly_disabled.amount.two_qualified,
            ],
            default=0,
        )

        # Limitations on under-65s

        is_elderly = person("age", period) >= elderly_disabled.age
        is_dependent = person("is_tax_unit_dependent", period)
        num_elderly = tax_unit.sum(is_elderly & ~is_dependent)
        disability_income = person("total_disability_payments", period)
        non_elderly_disability_income = tax_unit.sum(disability_income * ~is_elderly)

        cap = (
            num_elderly * elderly_disabled.amount.one_qualified
            + non_elderly_disability_income
        )

        capped_amount = min_(initial_amount, cap)
        total_pensions = add(tax_unit, period, ["pension_income"])
        taxable_pensions = add(tax_unit, period, ["taxable_pension_income"])
        non_taxable_pensions = total_pensions - taxable_pensions
        total_social_security = tax_unit("tax_unit_social_security", period)
        taxable_social_security = tax_unit("tax_unit_taxable_social_security", period)
        non_taxable_social_security = total_social_security - taxable_social_security
        # Section 22(c)(3)(A)(i)(II) reduces the amount by what the head or
        # spouse receives as a pension or annuity payable under the Railroad
        # Retirement Act of 1974 and excluded from gross income, whatever
        # provision excludes it: the tier 1 benefits section 86 leaves out,
        # and the tax-free part of the rest of the annuity, which 72(r)(2)
        # and 72(b) exclude as a recovery of the employee's tier 2 taxes.
        # Schedule R's line 13b keeps returns of cost out; the model follows
        # the statute's words.
        non_taxable_tier_1 = tax_unit(
            "tax_unit_railroad_social_security_equivalent_benefits_for_taxability",
            period,
        ) - tax_unit(
            "tax_unit_taxable_railroad_social_security_equivalent_benefits", period
        )
        non_taxable_tier_2 = tax_unit_non_dep_add(
            tax_unit, period, ["tax_exempt_railroad_pension_benefits"]
        )
        non_taxable_railroad = non_taxable_tier_1 + non_taxable_tier_2
        capped_reduced_amount = (
            capped_amount
            - non_taxable_pensions
            - non_taxable_social_security
            - non_taxable_railroad
        )
        agi = tax_unit("adjusted_gross_income", period)

        amount_over_phase_out = max_(
            0, agi - elderly_disabled.phase_out.threshold[filing_status]
        )
        phase_out_reduction = elderly_disabled.phase_out.rate * amount_over_phase_out

        amount = max_(0, capped_reduced_amount - phase_out_reduction)
        # Section 22(e)(1): a married individual filing a separate return
        # takes the credit only if the spouses lived apart for the whole
        # year. Schedule R gives a separate filer only boxes 8 and 9, both
        # conditioned on "you lived apart from your spouse for all of" the
        # year, so a separate filer who lived with the spouse has no line 19
        # section 22 amount. The bar sits here, not on the credit, so that
        # readers of the line 19 amount, such as Michigan's subtraction,
        # see it too.
        lived_together = tax_unit("cohabitating_spouses", period)
        return where(separate & lived_together, 0, amount)
