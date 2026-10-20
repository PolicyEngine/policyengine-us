from policyengine_us.model_api import *


class ia_liheap_fixed_income_only(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Iowa LIHEAP household has fixed income only"
    documentation = (
        "Whether the household has a fixed income source (Social Security, SSI, "
        "pensions including railroad retirement, or veterans' benefits) and no "
        "other recorded income source, across all members regardless of age. "
        'Definitions, Fixed Income Household: \'Only mark "fixed income" when '
        "that is the ONLY source(s) of income.' Recorded sources include the "
        "countable earned and unearned sources and two that Iowa does not count "
        "but calls not fixed: child support received and FIP. Under-18 income "
        "is excluded from the countable amount, but a minor's Social Security "
        "still identifies the household's income source: Appendix C records "
        "such payments at $0.00 'to capture source of income for AE fixed "
        "income criteria', and Section 4.40(3)(a) says they 'can still qualify "
        "the household' when that is the only source of income. A household "
        "with no recorded income source is not fixed income only."
    )
    reference = (
        # Section 4.40 item 3a; Definitions, Fixed Income Household; Appendix C
        # notes that alimony, variable annuities, child support and FIP are
        # not fixed income, Pensions and Railroad Retirement rows and Social
        # Security Benefits margin note; Appendix I, Fixed Income Only (no
        # other sources of income).
        # PDF pages 14, 81, 90-92, 98, 109-110, 114, 137
        "https://hhs.iowa.gov/media/17262/download?inline#page=14",
    )
    defined_for = StateCode.IA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ia.hhs.liheap.income.sources
        person = spm_unit.members
        # Definitions, Fixed Income Household (page 81): SSA, SSI, SSDI,
        # veterans' benefits and pensions. Section 4.40(3)(a) (page 14) and
        # Appendix C (page 114): a minor's Social Security still identifies a
        # fixed source, so no age gate applies here.
        fixed = add(spm_unit, period, p.fixed)
        # Every other recorded source of every member defeats the factor:
        # Appendix I reads "Fixed Income Only (no other sources of income)"
        # (page 137) and the Definitions say "Only mark 'fixed income' when
        # that is the ONLY source(s) of income" (page 81), which the formula
        # follows for FY2026. The FY27 manual and Program Notice 27-01
        # (effective October 1, 2026) reword the factor to "no other countable
        # sources of income"; that change is not modeled because only FY2026
        # is verified. Earned sources are floored per source as in the
        # countable amount. Appendix C adds that child support (page 92) and
        # FIP (page 98) are not fixed income although neither is counted.
        earned = 0
        for source in p.earned:
            earned = earned + max_(person(source, period), 0)
        other_unearned = [source for source in p.unearned if source not in p.fixed]
        non_fixed = (
            spm_unit.sum(earned)
            + add(spm_unit, period, other_unearned)
            + add(spm_unit, period, p.other_recorded)
        )
        return (fixed > 0) & (non_fixed == 0)
