from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicaid.income._apply_medicaid_optional_senior_or_disabled_exclusions import (
    _apply_medicaid_optional_senior_or_disabled_exclusions,
)
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_couple_income,
    _ssi_couple_total,
    _ssi_spouse_index,
)
from policyengine_us.variables.gov.states.il.dhs.aabd.income.expense._child_care_exemption import (
    il_aabd_child_care_exemption,
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
        # NOTE: this annual formula applies one couple status to the whole
        # year (couple_computation below), so it combines the spouses' annual
        # income by that same status. ssi_marital_earned_income and
        # ssi_marital_unearned_income are monthly and follow each month's
        # status; their annual totals would not match it in a year with a
        # part-year facility stay.
        pre_reduction_earned_income = _ssi_couple_income(
            person, period, "ssi_earned_income"
        )
        blind_disabled_working_student_income = person(
            "ssi_blind_or_disabled_working_student_exclusion", period
        )
        earned_income = max_(
            pre_reduction_earned_income - blind_disabled_working_student_income,
            0,
        )

        total_unearned_income = (
            _ssi_couple_income(person, period, "ssi_unearned_income")
            + person(
                "medicaid_optional_senior_or_disabled_unearned_income_deemed_from_ineligible_parent",
                period,
            )
            + person("ssi_in_kind_support_and_maintenance", period)
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
        # 120.370(a) exempts employment expenses. Child care is figured from
        # costs before subsidies: childcare_expenses nets out child care
        # subsidies, Pennsylvania's subsidy reads medical premiums, and those
        # read the Medicare Part B premium and through it Medicaid's buy-in,
        # so reading it here would make this variable depend on itself.
        # NOTE: a family with a child care subsidy also has the subsidized
        # part exempted.
        il_other_expenses = add(
            person,
            period,
            [
                source
                for source in il_aabd.exemption.sources
                if source != "il_aabd_child_care_expense_exemption"
            ],
        )
        il_monthly_child_care_costs = (
            person.spm_unit.sum(person("pre_subsidy_childcare_expenses", period))
            / MONTHS_IN_YEAR
        )
        il_child_care = sum(
            il_aabd_child_care_exemption(
                person, month, parameters, il_monthly_child_care_costs
            )
            for month in period.get_subperiods(MONTH)
        )
        il_expenses = (il_other_expenses + il_child_care) / MONTHS_IN_YEAR
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
        # Only a Part B enrollee (medicare_part_b_enrolled) has a Part B
        # premium to disregard.
        # NOTE: ACWDL 20-24 Example 5 also deducts a non-applicant spouse's
        # premiums. Spousal income here follows SSI deeming (20 CFR 416.1163),
        # so that premium is not modeled, nor is MC 176's maintenance need
        # deduction for the spouse (lines 19 and 21; issue 10543).
        # Premiums are counted before the Medicaid Part B buy-in, which starts
        # only once Medicaid finds the person eligible (42 USC 1395v(d)(2)(C)).
        part_b_enrolled = person("medicare_part_b_enrolled", period)
        paid_premiums = person("medicaid_eligibility_health_insurance_premiums", period)
        paid_part_b = (
            person("medicare_part_b_premium_before_buy_in", period) * part_b_enrolled
        )
        full_part_b = person("gross_medicare_part_b_premium", period) * part_b_enrolled
        disregards_part_b = p.disregards_medicare_part_b_premium[state].astype(bool)
        own_premiums = where(
            disregards_part_b,
            max_(paid_premiums - paid_part_b, 0) + full_part_b,
            paid_premiums,
        )
        # 22 CCR 50555.2(a) deducts premiums paid by and purchased for any
        # person in the family. A couple's budget takes both spouses'
        # premiums and, when the couple head their tax unit, those of its
        # unmarried tax dependents, whatever marital unit those dependents
        # are in: a child never shares a couple's marital unit. Spouses who
        # file separately each take the dependents of both tax units, so the
        # two halves of the budget agree. Another couple's dependent and an
        # unrelated adult in another tax unit stay out, as do the other
        # dependents of a tax unit the couple belong to as dependents.
        spouse = _ssi_spouse_index(person, period)
        safe_spouse = np.maximum(spouse, 0)
        unmarried_dependent = person("is_tax_unit_dependent", period) & (spouse < 0)
        dependents_premiums = where(
            person("is_tax_unit_head_or_spouse", period),
            person.tax_unit.sum(where(unmarried_dependent, own_premiums, 0)),
            0,
        )
        tax_unit_id = person.tax_unit.reference_entity.members_entity_id
        spouse_in_another_tax_unit = (spouse >= 0) & (
            tax_unit_id[safe_spouse] != tax_unit_id
        )
        family_dependents_premiums = dependents_premiums + where(
            spouse_in_another_tax_unit, dependents_premiums[safe_spouse], 0
        )
        premiums = where(
            couple_computation,
            _ssi_couple_total(person, period, own_premiums)
            + family_dependents_premiums,
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
