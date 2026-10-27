from policyengine_us.model_api import *


class nh_fap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "New Hampshire FAP countable income"
    reference = (
        # PDF pages 13-17,23,25-29,34-36.
        "https://www.energy.nh.gov/sites/g/files/ehbemt551/files/inline-documents/sonh/fuel-assistance-program-procedures-manual.pdf#page=13",
        # Plan item 1.9: Social Security "Excluding MediCare deduction";
        # General Assistance benefits unchecked.
        "https://liheapch.acf.gov/docs/2026/state-plans/NH_Plan_2026.pdf#page=6",
    )
    defined_for = StateCode.NH

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nh.doe.fap.income
        person = spm_unit.members
        # Annual inputs approximate application-period income annualization.
        # Separate business losses cannot offset positive sources. Existing
        # net inputs lack depreciation, amortization and home-business addbacks;
        # partnership/S-corporation inputs also lack FAP expense detail.
        business_income = 0
        for source in p.business_sources:
            business_income = business_income + max_(person(source, period), 0)
        # Military basic pay is part of employment_income, the convention under
        # which Virginia and Indiana subtract military_basic_pay from AGI, so it
        # is not added again.
        earned_income = max_(person("employment_income", period), 0) + business_income
        # Secondary school also includes equivalent training in the model;
        # this conjunction approximates the full-time high-school exclusion.
        high_school_student = person("is_full_time_student", period) & person(
            "is_in_secondary_school", period
        )
        countable_earnings = spm_unit.sum(where(high_school_student, 0, earned_income))
        unearned_person = 0
        for source in p.unearned_sources:
            # add() also sums monthly sources such as nh_ssp over the year.
            unearned_person = unearned_person + max_(add(person, period, [source]), 0)
        unearned_income = spm_unit.sum(unearned_person)
        adult_ssi = spm_unit.sum(
            where(
                person("age", period) >= p.ssi_min_age,
                person("ssi", period),
                0,
            )
        )
        # Apply one exclusion to combined interest and dividends per SPM unit;
        # the parameter comment gives the source basis.
        interest = max_(add(spm_unit, period, ["interest_income"]), 0)
        dividends = max_(add(spm_unit, period, ["ordinary_dividend_income"]), 0)
        investment_income = max_(interest + dividends - p.investment_disregard, 0)
        # Count received FANF once per SPM unit, respecting TANF take-up.
        income = (
            countable_earnings
            + unearned_income
            + adult_ssi
            + investment_income
            + spm_unit("tanf", period)
        )
        # Support-paid regularity and mileage reimbursements are not observed.
        support_paid = add(spm_unit, period, ["child_support_expense"])
        # Page 17 deducts "Medicare deductions from Social Security or Railroad
        # Retirement benefits (Part B and Part D)". Each member's out-of-pocket
        # Part B premium (zero when not enrolled or when a Medicare Savings
        # Program pays it) is deducted up to the Social Security and railroad
        # retirement benefits it is withheld from. No Part D premium variable
        # exists, so Part D is not deducted.
        withholding_benefits = max_(person("social_security", period), 0) + max_(
            person("railroad_benefits", period), 0
        )
        medicare_deduction = spm_unit.sum(
            min_(person("medicare_part_b_premium", period), withholding_benefits)
        )
        return max_(income - support_paid - medicare_deduction, 0)
