from policyengine_us.model_api import *


class ia_liheap_fixed_income_only(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Iowa LIHEAP household has fixed income only"
    documentation = (
        "Whether every recorded income source of the household, across all "
        "members regardless of age, is Social Security, SSI, veterans' benefits "
        "or pensions. Definitions, Fixed Income Household: 'Only mark \"fixed "
        "income\" when that is the ONLY source(s) of income.' Under-18 income "
        "is excluded from the countable amount, but a minor's Social Security "
        "still identifies the household's income source: Appendix C records "
        "such payments at $0.00 'to capture source of income for AE fixed "
        "income criteria', and Section 4.40(3)(a) says they 'can still qualify "
        "the household' when that is the only source of income. A household "
        "with no recorded income source is not fixed income only."
    )
    reference = (
        # Definitions, Fixed Income Household (page 81); Section 4.40 item 3a
        # (page 14); Appendix C Social Security Benefits margin note (page 114);
        # Appendix I, Fixed Income Only (no other sources of income) (page 137);
        # Appendix C notes that alimony, variable annuities and child support
        # are not fixed income (pages 90-92).
        "https://hhs.iowa.gov/media/17262/download?inline#page=81",
    )
    defined_for = StateCode.IA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ia.hhs.liheap.income
        person = spm_unit.members
        # Every recorded source of every member counts toward the test, with
        # no age gate; earned sources are floored per source as in the
        # countable amount.
        earned = 0
        for source in p.sources.earned:
            earned = earned + max_(person(source, period), 0)
        unearned = add(person, period, p.sources.unearned)
        recorded = spm_unit.sum(earned + unearned)
        # sources/fixed.yaml lists the fixed sources in the same relative order
        # as sources/unearned.yaml, so the two sums are bit-identical when every
        # other source is zero.
        fixed = spm_unit.sum(add(person, period, p.sources.fixed))
        return (fixed > 0) & (fixed == recorded)
