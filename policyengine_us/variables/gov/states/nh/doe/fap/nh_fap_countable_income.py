from policyengine_us.model_api import *


class nh_fap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "New Hampshire FAP countable income"
    reference = "https://www.energy.nh.gov/sites/g/files/ehbemt551/files/inline-documents/sonh/fuel-assistance-program-procedures-manual.pdf#page=13, 14, 15, 16, 17, 23, 25, 26, 27, 28, 29, 34, 35, 36"
    defined_for = StateCode.NH

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nh.doe.fap.income
        person = spm_unit.members
        # Annual inputs approximate application-period income annualization.
        # Separate business losses cannot offset positive sources. Existing
        # net inputs lack depreciation, amortization and home-business addbacks;
        # partnership/S-corporation inputs also lack FAP expense detail.
        business_income = sum(
            max_(person(source, period), 0) for source in p.business_sources
        )
        earned_income = max_(person("employment_income", period), 0) + business_income
        # Secondary school also includes equivalent training in the model;
        # this conjunction approximates the full-time high-school exclusion.
        high_school_student = person("is_full_time_student", period) & person(
            "is_in_secondary_school", period
        )
        countable_earnings = spm_unit.sum(where(high_school_student, 0, earned_income))
        unearned_income = spm_unit.sum(
            sum(max_(person(source, period), 0) for source in p.unearned_sources)
        )
        adult_ssi = spm_unit.sum(
            where(
                person("age", period) >= p.ssi_min_age,
                person("ssi", period),
                0,
            )
        )
        # Page 16 separately excludes the first $50 of each source; page 17's
        # "and/or" summary is ambiguous. Apply each exclusion once per household
        # source, not per person. This interpretation lacks agency confirmation.
        interest = add(spm_unit, period, ["interest_income"])
        dividends = add(spm_unit, period, ["ordinary_dividend_income"])
        investment_income = max_(interest - p.investment_disregard, 0) + max_(
            dividends - p.investment_disregard, 0
        )
        # FANF is an SPM-unit benefit and is counted once. Gross Social Security
        # and Railroad Retirement remain counted: Medicare B/D reconstruction
        # is deferred. Support-paid regularity and mileage reimbursements are
        # not separately observed; only reported support is deducted.
        income = (
            countable_earnings
            + unearned_income
            + adult_ssi
            + investment_income
            + spm_unit("nh_fanf", period)
        )
        support_paid = add(spm_unit, period, ["child_support_expense"])
        return max_(income - support_paid, 0)
