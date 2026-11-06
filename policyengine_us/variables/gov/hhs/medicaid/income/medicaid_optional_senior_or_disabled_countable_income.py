from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicaid.income._apply_medicaid_optional_senior_or_disabled_exclusions import (
    _apply_medicaid_optional_senior_or_disabled_exclusions,
)


class medicaid_optional_senior_or_disabled_countable_income(Variable):
    value_type = float
    entity = Person
    label = "Countable income for Medicaid's optional senior or disabled pathway"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1396a#m",
        "https://www.law.cornell.edu/cfr/text/42/435.601",
        "https://www.kff.org/medicaid/medicaid-financial-eligibility-for-seniors-and-people-with-disabilities-findings-from-a-50-state-survey/",
        # Missouri MHABD budgeting order and rounding
        "https://dssmanuals.mo.gov/mo-healthnet-for-the-aged-blind-and-disabled/0805-000-00/0805-015-00/",
        "https://dssmanuals.mo.gov/mo-healthnet-for-the-aged-blind-and-disabled/0805-000-00/0805-015-00/0805-015-25/",
        "https://dssmanuals.mo.gov/mo-healthnet-for-the-aged-blind-and-disabled/0805-000-00/0805-015-00/0805-015-40/",
        # California ABD FPL disregard and Part B and health insurance premium
        # deductions
        "https://www.dhcs.ca.gov/services/medi-cal/eligibility/letters/Documents/c00-57.pdf#page=3",
        "https://www.dhcs.ca.gov/services/medi-cal/eligibility/letters/Documents/20-24.pdf#page=3",
        "https://www.dhcs.ca.gov/services/medi-cal/eligibility/letters/Documents/20-18.pdf#page=2",
        "https://www.law.cornell.edu/regulations/california/22-CCR-50555.2",
        "https://www.law.cornell.edu/uscode/text/42/1395r#i",
        "https://www.law.cornell.edu/cfr/text/20/416.1163",
        # Illinois MANG(AABD) unearned income, exemptions and employment expenses
        "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-120.330",
        "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-120.335",
        "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-120.340",
        "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-120.360",
        "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-120.362",
        "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-120.370",
        # Section 209(b) states deduct SSI payments from income
        "https://www.law.cornell.edu/cfr/text/42/435.121",
    )

    def formula(person, period, parameters):
        pre_reduction_earned_income = person("ssi_marital_earned_income", period)
        blind_disabled_working_student_income = person(
            "ssi_blind_or_disabled_working_student_exclusion", period
        )
        earned_income = max_(
            pre_reduction_earned_income - blind_disabled_working_student_income,
            0,
        )

        total_unearned_income = add(
            person,
            period,
            [
                "ssi_marital_unearned_income",
                "medicaid_optional_senior_or_disabled_unearned_income_deemed_from_ineligible_parent",
                "ssi_in_kind_support_and_maintenance",
            ],
        )

        couple_computation = person("ssi_couple_computation_applies", period)
        state = person.household("state_code_str", period)
        p = parameters(
            period
        ).gov.hhs.medicaid.eligibility.categories.senior_or_disabled.income
        income_disregard = where(
            couple_computation,
            p.disregard.couple[state],
            p.disregard.individual[state],
        )
        personal_countable = _apply_medicaid_optional_senior_or_disabled_exclusions(
            earned_income,
            total_unearned_income,
            state,
            income_disregard,
            parameters,
            period,
        )
        # Illinois budgets MANG(AABD) income by its own rules (89 Ill. Adm. Code
        # 120). 120.330(a) counts all unearned income not specified as exempt, so
        # sources on SSI's list that AABD's list leaves out, such as pensions,
        # count too. Rent counts as unearned: 120.360(b) limits earned income to
        # wages and self-employment profits. A loss on one source is not income
        # and does not reduce another. In-kind income does not count: "Unearned
        # income in-kind shall be exempt" (120.340(b)). AABD's list includes SSI,
        # which 42 CFR 435.121(f)(1)(i) deducts.
        # NOTE: There is no input for actively managing a property, so a
        # self-employed landlord's rent also counts as unearned.
        gov = parameters(period).gov
        il_aabd = gov.states.il.dhs.aabd.income
        il_other_sources = [
            source
            for source in gov.ssa.ssi.income.sources.unearned
            if source not in il_aabd.sources.earned
            and source not in il_aabd.sources.unearned
        ]
        il_unearned = (
            max_(
                sum(
                    max_(add(person, period, [source]), 0)
                    for source in [
                        *il_aabd.sources.unearned,
                        *il_other_sources,
                        "rental_income",
                    ]
                )
                - person("ssi", period),
                0,
            )
            / MONTHS_IN_YEAR
        )
        # A client has "only one $25.00 exemption" (120.335(a)(1)). It comes off
        # income other than SSI, unearned first and then earnings.
        il_flat = il_aabd.exemption.flat
        il_flat_on_earnings = max_(il_flat - il_unearned, 0)
        il_earnings = (
            max_(
                add(person, period, ["il_aabd_gross_earned_income"])
                - person("rental_income", period),
                0,
            )
            / MONTHS_IN_YEAR
        )
        # 120.370(a) exempts employment expenses.
        il_expenses = (
            add(person, period, ["il_aabd_expense_exemption_person"]) / MONTHS_IN_YEAR
        )
        # 120.362(b) exempts "the first $20.00 of gross earned income and one-half
        # of the next $60.00" or, for blind people, "The first $85.00 of the gross
        # earned income and one-half of the amount in excess of $85.00".
        il_earned_exemption = where(
            person("is_blind", period),
            il_aabd.exemption.blind.calc(il_earnings),
            il_aabd.exemption.elderly_or_disabled.calc(il_earnings),
        )
        il_own_countable = (
            max_(il_unearned - il_flat, 0)
            + max_(
                il_earnings - il_earned_exemption - il_expenses - il_flat_on_earnings,
                0,
            )
        ) * MONTHS_IN_YEAR
        il_countable = where(
            couple_computation,
            person.marital_unit.sum(il_own_countable),
            il_own_countable,
        ) + person(
            "medicaid_optional_senior_or_disabled_unearned_income_deemed_from_ineligible_parent",
            period,
        )
        personal_countable = where(state == "IL", il_countable, personal_countable)

        # 22 CCR 50555.2 deducts person-paid premiums, Part B only when the
        # person pays it. From 12/2020 (ACWDL 20-18, 20-24) CA disregards Part B
        # "regardless of how the premium is paid": swap the person-paid Part B
        # in the shared aggregate for the individual's full Part B premium, the
        # base premium plus any IRMAA (42 USC 1395r(i)), whoever pays it.
        # NOTE: medicare_enrolled (Part A and/or Part B) stands in for Part B
        # enrollment, as in medical_expense_health_insurance_premiums.
        # NOTE: ACWDL 20-24 Example 5 also deducts a non-applicant spouse's
        # premiums. Spousal income here follows SSI deeming (20 CFR 416.1163),
        # so that premium is not modeled, nor is MC 176's maintenance need
        # deduction for the spouse (lines 19 and 21; issue 10543).
        medicare_enrolled = person("medicare_enrolled", period)
        paid_premiums = person("medical_expense_health_insurance_premiums", period)
        paid_part_b = person("medicare_part_b_premium", period) * medicare_enrolled
        full_part_b = (
            person("gross_medicare_part_b_premium", period) * medicare_enrolled
        )
        disregards_part_b = p.disregards_medicare_part_b_premium[state].astype(bool)
        own_premiums = where(
            disregards_part_b,
            max_(paid_premiums - paid_part_b, 0) + full_part_b,
            paid_premiums,
        )
        premiums = where(
            couple_computation,
            person.marital_unit.sum(own_premiums),
            own_premiums,
        )
        deducts_premiums = p.deducts_health_insurance_premiums[state].astype(bool)
        # MC 176 (ACWDL 00-57) lines 16-17 subtract the additional disregard
        # and the premiums from income after the SSI exclusions.
        additional_disregard = (
            where(
                couple_computation,
                p.additional_disregard.couple[state],
                p.additional_disregard.individual[state],
            )
            * MONTHS_IN_YEAR
        )
        deductions = where(deducts_premiums, premiums, 0) + additional_disregard

        spousal_deemed = person(
            "medicaid_optional_senior_or_disabled_income_deemed_from_ineligible_spouse",
            period,
        )
        # SSI methodology (42 CFR 435.601) counts the applicant's own income
        # whether or not they meet SSI's noncitizen rules. People who are not
        # aged, blind, or disabled have no countable income here; a spouse's
        # income is deemed to the applicant instead.
        is_aged_blind_disabled = person("is_ssi_aged_blind_disabled", period)

        # ACWDL 20-24 Examples 2 and 5 combine the non-applicant spouse's
        # income with the applicant's income before the deductions, as
        # 20 CFR 416.1163(d)(2) does, so subtract the deductions from the
        # combined income and floor the result.
        countable = where(
            couple_computation,
            max_(personal_countable - deductions, 0) / 2,
            max_(personal_countable + spousal_deemed - deductions, 0),
        )
        return where(is_aged_blind_disabled, countable, 0)
