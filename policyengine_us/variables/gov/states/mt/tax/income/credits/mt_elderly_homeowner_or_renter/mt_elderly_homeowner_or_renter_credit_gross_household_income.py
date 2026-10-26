from policyengine_us.model_api import *
from policyengine_us.variables.gov.irs.income.taxable_income.adjusted_gross_income.irs_gross_income.social_security.dependent_taxable_ss_magi import (
    PERSON_ABOVE_THE_LINE_DEDUCTIONS,
)


class mt_elderly_homeowner_or_renter_credit_gross_household_income(Variable):
    value_type = float
    entity = Person
    label = "Montana gross household income for the elderly homeowner/renter credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT
    reference = (
        "https://law.justia.com/codes/montana/2022/title-15/chapter-30/part-23/section-15-30-2337/",
        "https://mca.legmt.gov/bills/mca/title_0150/chapter_0300/part_0230/section_0370/0150-0300-0230-0370.html",
        # 2023 Form 2 instructions, PDF pages 51-52: each household member's
        # return (line 1), nonfilers' wages (line 8), no losses (line 9).
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2023_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=51",
        # 2024 Schedule 2EC, line 17: income received by other members of
        # the household
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2024_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=48",
        # The statutory federal-AGI definition remains after the 2024 form
        # began displaying separate income categories: HB191 § 1(9), p.2.
        "https://archive.legmt.gov/bills/2021/HB0199/HB0191_X.pdf#page=2",
    )

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.mt.tax.income.credits.elderly_homeowner_or_renter
        sources = add(person, period, p.gross_income_sources)
        # Gross household income counts every member's federal AGI without
        # losses (§ 15-30-2337(4), (9)(a)). The dependent's gross income is
        # omitted from this return's AGI, but their own valid non-loss
        # adjustments still belong on their own return (2023 instructions,
        # line 1). Do not subtract the parent's TaxUnit-level deductions.
        ald = parameters(period).gov.irs.ald
        deduction_variables = [
            PERSON_ABOVE_THE_LINE_DEDUCTIONS[name]
            for name in ald.deductions
            if name in PERSON_ABOVE_THE_LINE_DEDUCTIONS
            and name not in ald.filer_amounts_recorded_on_dependents
        ]
        # The shared mapping uses capped/eligible person-level deductions,
        # including the dependent's own IRA deduction. It excludes loss_ald:
        # business/capital losses never reduce Montana household income.
        # Parent-owned adoption/bond exclusions recorded on dependents
        # remain with the filer under the existing convention.
        own_deductions = add(person, period, deduction_variables)
        is_dependent = person("is_tax_unit_dependent", period)
        dependent_income = is_dependent * (
            person("dependent_gross_income", period) - own_deductions
        )
        # The income above counts only the taxable portion of Social
        # Security: a filer's in federal AGI (irs_gross_income counts people
        # who are not dependents), a dependent's in their own gross income
        # (dependent_gross_income counts people who are not the head or
        # spouse). Subtract only the part one of them counted, then add the
        # rest, so all SS is counted once per § 15-30-2337(9)(a)(viii) even
        # when a person is input as both a dependent and the head.
        social_security = person("social_security", period)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        counted_social_security = where(
            is_dependent,
            ~head_or_spouse * person("dependent_taxable_social_security", period),
            person("taxable_social_security", period),
        )
        untaxed_social_security = max_(social_security - counted_social_security, 0)
        # Income is federal AGI "without regard to loss" (§ 15-30-2337(9)(a)),
        # so the business and capital losses deducted in computing federal
        # AGI are added back (2023 Elderly Homeowner/Renter Credit Schedule,
        # line 9: "The gross household income cannot be reduced by any
        # losses."). The return's losses are added once, to the head.
        head = person("is_tax_unit_head", period)
        losses = head * person.tax_unit("loss_ald", period)
        # Count each person's capital gains without losses, as 2024 Schedule
        # 2EC line 7 requires ("do not include any capital losses"). Two
        # losses reduce the gains the income paths count without reaching
        # loss_ald, which holds only the capital loss deducted in AGI:
        # - a short-term loss netted against the same person's long-term gain
        #   (or the reverse) inside capital_gains;
        # - the prior-year long-term capital loss carryover, which
        #   long_term_capital_gains already includes as a loss, as Schedule D
        #   line 15 does. Adding it back gives the year's own long-term gain
        #   (as az_property_tax_credit_capital_gains does); only the gain it
        #   hid is restored, never the unused loss.
        # The long-term and short-term parts, when either is nonzero, decide
        # the gains: max(0, long-term + carryover) + max(0, short-term).
        # capital_gains can disagree with them: once it is an input for
        # anyone in a simulation, everyone without one holds its default of
        # zero, not the sum of their parts. Without parts, capital_gains is a
        # net amount supplied directly, and the gain is max(0, net +
        # carryover); the carryover is never counted as a gain the parts did
        # not show.
        carryover = max_(0, person("long_term_capital_loss_carryover", period))
        long_term_capital_gains = person("long_term_capital_gains", period)
        short_term_capital_gains = person("short_term_capital_gains", period)
        short_term_gains = max_(0, short_term_capital_gains)
        capital_gains = person("capital_gains", period)
        parts_supplied = (long_term_capital_gains != 0) | (
            short_term_capital_gains != 0
        )
        gains_without_losses = where(
            parts_supplied,
            max_(0, long_term_capital_gains + carryover) + short_term_gains,
            max_(0, capital_gains + carryover),
        )
        # The gains each income path already counted: irs_gross_income
        # floors the net, dependent_gross_income floors each part. The
        # difference replaces them with the gains above; it is negative only
        # when an inconsistent capital_gains input exceeds the parts. A person
        # input as both a dependent and the head is counted by neither path,
        # so nothing is restored for them.
        counted_gains = where(
            is_dependent,
            ~head_or_spouse
            * max_(
                max_(0, long_term_capital_gains) + short_term_gains,
                capital_gains,
            ),
            max_(0, capital_gains),
        )
        counted_by_a_path = ~(is_dependent & head_or_spouse)
        lost_capital_gains = counted_by_a_path * (gains_without_losses - counted_gains)
        return (
            sources
            + dependent_income
            + untaxed_social_security
            + losses
            + lost_capital_gains
        )
