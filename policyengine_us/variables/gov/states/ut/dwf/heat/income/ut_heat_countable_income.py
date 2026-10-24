from policyengine_us.model_api import *


class ut_heat_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Utah HEAT annual countable household income"
    defined_for = StateCode.UT
    reference = (
        "https://jobs.utah.gov/infosource/heatpolicy/Policy/Obsolete_Policy/Obsolete_400/Obsolete_401_(10_1_24_to_9_30_26)_Income.htm",
        "https://jobs.utah.gov/infosource/heatpolicy/Policy/400_Income_Standards/402_Unearned_Income.htm",
        "https://jobs.utah.gov/infosource/heatpolicy/Policy/400_Income_Standards/404_Self-Employment/404_Self-Employment.htm",
        "https://jobs.utah.gov/infosource/heatpolicy/Policy/Obsolete_Policy/Obsolete_400/Obsolete_405_(3_1_25_to_9_30_26)_Income_Exclusions.htm",
        "https://jobs.utah.gov/infosource/heatpolicy/Policy/Obsolete_Policy/Obsolete_400/Obsolete_407_(3_1_26_to_9_30_26)_Qualified_Deductions.htm",
        "https://jobs.utah.gov/infosource/heatpolicy/Policy/400_Income_Standards/406_No_Longer_Applicable.htm",
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
        # Earned income counts in full, following manual sections 401 and 406
        # (income disregards obsolete since September 30, 2023) and the March
        # 2026 worksheet. Utah Admin. Code R982-403-6 disregards 20% of earned
        # income, as do manual section 204 and the FY2026 benefit matrix
        # workbook.
        wages = max_(person("employment_income", period), 0)
        business = add(person, period, p.business_income_sources)
        rental = max_(person("rental_income", period), 0) + max_(
            person("farm_rent_income", period), 0
        )
        # Existing net business inputs stand for current net amounts. They do
        # not reconstruct HEAT expenses or isolate disallowed prior-period
        # losses. Current reported losses enter the household total; rental
        # losses do not. No business expense or insurance is deducted twice.
        unearned = sum(
            max_(person(source, period), 0) for source in p.unearned_income_sources
        )
        gross = spm_unit.sum(
            where(excluded_child, 0, wages + business + rental + unearned)
        )
        # Child support belongs on the receiving parent. TANF/FEP/GA, ordinary
        # bank interest, educational aid and exempt nonrecurring receipts are
        # excluded. Broad inputs cannot isolate all exempt gifts, settlements,
        # combat pay, third-party payments, or cash withdrawals from trusts.
        premiums = person("health_insurance_premiums", period)
        # A positive aggregate premium already includes reported components.
        # Otherwise use both reported components without deriving Medicare.
        reported_premiums = where(
            premiums > 0,
            premiums,
            max_(
                person("health_insurance_premiums_without_medicare_part_b", period),
                0,
            )
            + max_(person("medicare_part_b_premiums_reported", period), 0),
        )
        medical = spm_unit.sum(
            max_(reported_premiums, 0)
            + max_(person("pre_tax_health_insurance_premiums", period), 0)
            + max_(person("other_medical_expenses", period), 0)
        )
        support_paid = add(
            spm_unit, period, ["child_support_expense", "alimony_expense"]
        )
        # Reported medical costs approximate qualified uncompensated payments;
        # Medicare premiums are not derived. Self-employed premiums must be
        # included only once. Support to an included child, payment timing and
        # medical-purpose restrictions are not identified by these inputs.
        # The seasonal equipment deduction is outside the heating-bill scope.
        return max_(gross - medical - max_(support_paid, 0), 0)
