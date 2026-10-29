from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.ia.hhs.ssa._ia_ssa_smme_spouse_income import (
    ia_ssa_smme_spouse_is_sga_applicant,
)


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
        # 8-E Deeming from an Ineligible Spouse; PDF pages 12-13
        "https://hhs.iowa.gov/media/4011/download?inline#page=12",
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
        # rule and Iowa Code 249.12(3), under which privately operated
        # facilities "shall be reimbursed based on the maximum per diem rates
        # established by the general assembly", and pays the maximum rate
        # unless a lower facility rate is entered (ia_ssa.yaml Cases 14, 15
        # and 56).
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
        # the rule's fixed amount (ia_ssa.yaml Cases 52-53).
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
        # not other income here (ia_ssa.yaml Case 63).
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
        # the poverty guideline. 6-B p.77 determines income "according to SSI
        # income criteria", and 8-E p.12 says to "Process as a one-person
        # household" when SSI deems nothing from an ineligible spouse. So the
        # guideline is for two people only when SMME income includes a
        # spouse's income: an eligible couple's combined income, or income
        # deemed from a spouse, by SSI or, for an applicant working above the
        # SGA level, by ia_ssa_smme_spousal_deeming_applies (a spouse's income
        # above the couple rate less the individual rate, or the income of a
        # spouse who is not an ineligible spouse), or, for the aged, blind or
        # disabled spouse of such an applicant, the couple's combined income
        # (for example ia_ssa.yaml Cases 47-49, 82, 84, 97 and 102-105; Cases
        # 83, 92, 96 and 99 use the one-person guideline).
        # NOTE: SSI's deeming and couple computation, read here and in
        # ia_ssa_smme_countable_income for anyone SSI counts, do not yet stop
        # for an applicant at the $30 facility rate (20 CFR 416.1163(f)(5)),
        # for a spouse who is not aged, blind or disabled and has entered a
        # medical facility, or for a spouse in a privately paid facility (20
        # CFR 416.1167, 416.1149, 416.1801(c); issue 10455), so the SSI
        # path can still combine or deem in those households (Case 81 is the
        # Medicaid-paid stay, which SSI separates).
        spouse_income = (
            joint
            | person("is_ssi_spousal_deeming_applies", period.this_year)
            | person("ia_ssa_smme_spousal_deeming_applies", period)
            | ia_ssa_smme_spouse_is_sga_applicant(person, period)
        )
        size = where(spouse_income, 2, 1)
        # 441 IAC 75.1 revises the federal poverty level "annually on April 1",
        # so earlier months use the prior year's guidelines (Cases 78-80).
        year = period.start.year
        if period.start.month < p.fpg_year_start_month:
            year = year - 1
        fpg = parameters(f"{year}-01-01").gov.hhs.fpg
        poverty = (
            fpg.first_person.CONTIGUOUS_US
            + (size - 1) * fpg.additional_person.CONTIGUOUS_US
        ) / MONTHS_IN_YEAR
        # NOTE: Iowa Code 249.3(4)(g) requires "income of at least one hundred
        # twenty percent of the federal poverty level". 441 IAC 51.7(6) says
        # income "must exceed 120 percent of the federal poverty level", and
        # 6-B Income (SMME) p.77 says it "also exceeds 120% of the federal
        # poverty level". Where a statute and a rule or manual disagree, the
        # model follows the statute (the statute-first rule in CONTRIBUTING.md), so
        # income of exactly 120% qualifies and one cent less does not
        # (ia_ssa.yaml Cases 44-45).
        # Iowa Code 249.3(4)(c) limits SMME to a person who "Would be eligible
        # for supplemental security income benefits but for having excess
        # income or but for being engaged in substantial gainful activity and
        # having excess income", and 6-B p.74 pays it to "certain Medicaid
        # recipients who do not qualify for other cash assistance benefits".
        # So a person SSI pays gets no SMME, including the aged, blind or
        # disabled spouse of an applicant working above the SGA level, whom
        # SSI still pays after deeming from that applicant (Case 110).
        smme = (
            person("ia_ssa_smme_coverage_eligible", period)
            & (
                person("ia_ssa_smme_countable_income", period)
                >= p.smme_minimum_fpg_rate * poverty
            )
            & (federally_paid == 0)
            & (person("ssi_if_takes_up", period) == 0)
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
