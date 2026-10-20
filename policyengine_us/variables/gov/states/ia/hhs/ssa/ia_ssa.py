from policyengine_us.model_api import *


class ia_ssa(Variable):
    value_type = float
    entity = Person
    label = "Iowa State Supplementary Assistance"
    definition_period = MONTH
    unit = USD
    reference = (
        # Iowa Code 249.3; PDF pages 2-3
        "https://www.legis.iowa.gov/docs/code/249.pdf#page=2",
        # 441 IAC 51.4(3) and 51.7(6); PDF pages 1-2
        "https://www.legis.iowa.gov/docs/iac/chapter/441.51.pdf#page=1",
        # 441 IAC 52.1; PDF pages 1-2
        "https://www.legis.iowa.gov/docs/iac/chapter/441.52.pdf#page=1",
        # PDF pages 35, 41-49, 59-74, 76-78
        "https://hhs.iowa.gov/media/3987/download?inline=#page=35",
    )
    defined_for = "ia_ssa_eligible"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ia.hhs.ssa
        federal = parameters(period).gov.ssa.ssi
        category = person("ia_ssa_category", period)
        c = category.possible_values
        federally_paid = person("ia_ssa_federal", period)
        income = person("ia_ssa_care_countable_income", period)
        extra = max_(person("ia_ssa_care_additional_deductions", period), 0)
        partial = person("ia_ssa_care_partial_month_days", period)
        days = where(partial > 0, min_(partial, period.days), period.days)
        joint = person("ssi_couple_computation_applies", period)
        # NOTE: 441 IAC 52.1(3): "For periods of eligibility beginning July 1,
        # 2017, and thereafter, payment to a recipient in a licensed residential
        # care facility will be based on the maximum per diem rate", and 51.4(3)
        # tests income against "31 times the maximum per diem rate". 6-B
        # Billing and Payments p.72 still describes "two options": a
        # cost-related per diem rate "established by the Department
        # specifically for each facility" of up to $38.47, or "A flat per diem
        # rate ... $17.86 beginning February 1, 2004". The model follows the
        # rule and pays the maximum rate unless a lower facility rate is
        # entered (ia_ssa.yaml Cases 19, 20 and 68).
        entered_rate = max_(person("ia_ssa_rcf_daily_rate", period), 0)
        rate = where(
            entered_rate > 0,
            min_(entered_rate, p.rcf_daily_limit),
            p.rcf_daily_limit,
        )
        # 441 IAC 52.1(3)"a"(6): "The income of a resident who lived at home in
        # the month of entry will not be applied to the cost of care except to
        # the extent the income exceeds the SSI benefit for one person or for a
        # married couple if the resident also had a spouse living in the home
        # in the month of entry." In a couple-budget entry month
        # (ia_ssa_rcf_couple_budget) each spouse's care income is half the
        # couple's, so each deducts half the couple rate.
        # NOTE: 6-B First-Month Client Participation pp.63-64 deducts "the SSI
        # benefit rate for one person" or "for a married couple", as the rule
        # does, but later lets clients from an independent living arrangement
        # "keep enough of the first month's income to meet maintenance or
        # living expenses from the previous living arrangement, but do not
        # disregard an amount that is over the SSI standard". The model follows
        # the rule's fixed amount (ia_ssa.yaml Cases 64-65).
        has_spouse = person("ia_ssa_has_spouse", period)
        entry = where(has_spouse, federal.amount.couple, federal.amount.individual)
        entry = where(
            person("ia_ssa_rcf_couple_budget", period), entry / 2, entry
        ) * person("ia_ssa_care_initial_partial_month", period)
        rcf_participation = max_(income - p.rcf_personal_needs - extra - entry, 0)
        # Paying the covered days less participation, floored at zero, matches
        # the 51.4(3) income test in a 31-day month and pays nothing in a
        # shorter month that income covers (52.1(3)"d").
        rcf = max_(rate * days - rcf_participation, 0)
        ihhrc = person("ia_ssa_ihhrc_amount", period)
        # 6-B Making the Family-Life Home Payment: "For a recipient who has
        # only SSI and no other income (and hence no $20 to disregard), an
        # additional $20 payment is necessary". The $20 is SSI's general income
        # exclusion, so the federal parameter is used. Only positive amounts
        # count as other income, and the eligible couple shares one $20.
        receives_ssi = (person("ssi", period) > 0) | person("receives_ssi", period)
        sources = federal.income.sources
        # Interest and dividends are excluded from income as in
        # ia_ssa_care_countable_income (20 CFR 416.1124(c)(22)), so they are
        # not other income here (ia_ssa.yaml Case 77).
        excluded = p.excluded_unearned_sources
        has_other_income = np.zeros(person.count, dtype=bool)
        for source in list(sources.earned) + list(sources.unearned):
            if source not in excluded:
                has_other_income = has_other_income | (person(source, period) > 0)
        has_other_income = where(
            joint, person.marital_unit.any(has_other_income), has_other_income
        )
        flh = category == c.FAMILY_LIFE_HOME
        recipients = person.marital_unit.sum(flh)
        top_up = (
            ~has_other_income
            * receives_ssi
            * federal.income.exclusions.general
            / where(joint, max_(recipients, 1), 1)
        )
        # 441 IAC 51.7(6) and 6-B Income (SMME) p.77 set no family size for
        # the poverty guideline. The model uses the recipient and any spouse,
        # matching ia_ssa_smme_countable_income, which combines an eligible
        # couple's income.
        size = where(has_spouse, 2, 1)
        fpg = parameters(period).gov.hhs.fpg
        poverty = (
            fpg.first_person.CONTIGUOUS_US
            + (size - 1) * fpg.additional_person.CONTIGUOUS_US
        ) / MONTHS_IN_YEAR
        # NOTE: Iowa Code 249.3(4)(g) requires "income of at least one hundred
        # twenty percent of the federal poverty level", in a subsection that
        # opens "At the discretion of the department". 441 IAC 51.7(6) says
        # income "must exceed 120 percent of the federal poverty level", and
        # 6-B Income (SMME) p.77 says it "also exceeds 120% of the federal
        # poverty level". The model follows 51.7(6) and the manual, so income
        # of exactly 120% does not qualify (ia_ssa.yaml Cases 56-57).
        smme = (
            person("ia_ssa_smme_coverage_eligible", period)
            & (
                person("ia_ssa_smme_countable_income", period)
                > p.smme_minimum_fpg_rate * poverty
            )
            & (federally_paid == 0)
        )
        state = select(
            [
                category == c.RESIDENTIAL_CARE,
                category == c.IN_HOME_CARE,
                flh,
                category == c.SMME,
            ],
            [rcf, ihhrc, top_up, smme * p.smme_amount],
            default=0,
        )
        return federally_paid + state
