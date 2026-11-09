from policyengine_us.model_api import *


class ut_heat_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Utah HEAT annual countable household income"
    defined_for = StateCode.UT
    reference = (
        "https://www.law.cornell.edu/regulations/utah/Utah-Admin-Code-R982-403-2",
        "https://www.law.cornell.edu/regulations/utah/Utah-Admin-Code-R982-403-6",
        "https://www.law.cornell.edu/regulations/utah/Utah-Admin-Code-R982-403-7",
        "https://jobs.utah.gov/infosource/heatpolicy/Policy/Obsolete_Policy/Obsolete_400/Obsolete_401_(10_1_24_to_9_30_26)_Income.htm",
        "https://jobs.utah.gov/infosource/heatpolicy/Policy/400_Income_Standards/402_Unearned_Income.htm",
        "https://jobs.utah.gov/infosource/heatpolicy/Policy/400_Income_Standards/403_Earned_Income.htm",
        "https://jobs.utah.gov/infosource/heatpolicy/Policy/400_Income_Standards/404_Self-Employment/404_Self-Employment.htm",
        "https://jobs.utah.gov/infosource/heatpolicy/Policy/Obsolete_Policy/Obsolete_400/Obsolete_405_(3_1_25_to_9_30_26)_Income_Exclusions.htm",
        "https://jobs.utah.gov/infosource/heatpolicy/Policy/Obsolete_Policy/Obsolete_400/Obsolete_407_(3_1_26_to_9_30_26)_Qualified_Deductions.htm",
        "https://jobs.utah.gov/infosource/heatpolicy/Policy/200_Program_Standards/204_Eligibility_with_Ineligible_Resident.htm",
        "https://jobs.utah.gov/infosource/heatpolicy/assets/docs/Training/FY26/3.1.26%20Benefit%20Calculation%20Worksheet.xlsx",
        "https://liheapch.acf.gov/docs/2026/state-plans/UT_Plan_2026.pdf#page=6",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ut.dwf.heat.income
        person = spm_unit.members
        age = person("age", period)
        in_school = person("is_in_k12_school", period) | person(
            "is_in_secondary_school", period
        )
        excluded_child = (age < p.child_income_age) | (
            (age < p.student_income_age) & in_school
        )
        # Annual inputs approximate the preceding eligibility month. All
        # otherwise countable adult income counts regardless of immigration.
        # Each source is floored at zero, so a business or rental loss does
        # not offset other income. R982-403-6 disregards 20% of earned income,
        # including self-employment income after business costs; section 204
        # and the March 2026 worksheet (cell C8) apply the same disregard.
        earned = 0
        for source in p.earned_income_sources:
            earned = earned + max_(person(source, period), 0)
        unearned = 0
        for source in p.unearned_income_sources:
            unearned = unearned + max_(person(source, period), 0)
        counted = earned * (1 - p.earned_income_disregard) + unearned
        income = spm_unit.sum(where(excluded_child, 0, counted))
        # Child support belongs on the receiving parent. TANF/FEP/GA, ordinary
        # bank interest, educational aid and exempt nonrecurring receipts are
        # excluded. Broad inputs cannot isolate all exempt gifts, settlements,
        # combat pay, third-party payments, or cash withdrawals from trusts.
        # Section 407 and R982-403-7(1)(b) count health insurance premiums as
        # medical expenses. The premium aggregate takes a nonzero direct
        # premium input, or else non-Medicare premiums plus the modeled Part B
        # premium for enrollees net of Medicare Savings Program coverage; Part A
        # and pretax payroll premiums are added once each.
        medical = spm_unit.sum(
            max_(person("medical_expense_health_insurance_premiums", period), 0)
            + max_(person("pre_tax_health_insurance_premiums", period), 0)
            + person("medicare_part_a_premium", period)
            + max_(person("other_medical_expenses", period), 0)
        )
        support_paid = add(
            spm_unit, period, ["child_support_expense", "alimony_expense"]
        )
        # Reported medical costs approximate qualified uncompensated payments.
        # Self-employed premiums must be included only once. Support to an
        # included child, payment timing and medical-purpose restrictions are
        # not identified by these inputs. The seasonal equipment deduction is
        # outside the heating-bill scope.
        return max_(income - medical - max_(support_paid, 0), 0)
