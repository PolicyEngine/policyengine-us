from policyengine_us.model_api import *


class ri_liheap_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Rhode Island LIHEAP countable income"
    defined_for = StateCode.RI
    reference = (
        # Manual sections III.E-H, pages 14-21; plan sections 1.8-1.9, pages 5-7.
        "https://ripuc.ri.gov/eventsactions/docket/4290-DHS-DR-PUC%203-6%20attachment%20LIHEAP%20Manual%202020%20-%20Final.pdf#page=14",
        "https://liheapch.acf.gov/docs/2026/state-plans/RI_Plan_2026.pdf#page=5",
        "https://dhs.ri.gov/media/9671/download?language=en",
        "https://dhs.ri.gov/media/9701/download?language=en",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ri.dhs.liheap.income
        person = spm_unit.members
        age = person("age", period)
        # Retain the manual's head-of-household exception. The abbreviated
        # May 2025 instructions omit it without expressly repealing it;
        # the current treatment of student heads remains unverified.
        exempt_student = (
            (age < p.student_age_limit)
            & person("is_full_time_student", period)
            & ~person("is_household_head", period)
        )
        counted_person = (age >= p.minimum_income_age) & ~exempt_student
        # Existing net business receipts approximate the gross-receipts rule.
        # No additional 40% business deduction or new expense input is used.
        earnings = 0
        for source in p.sources.earned:
            earnings = earnings + max_(person(source, period), 0)
        # ADD annualizes monthly SSI before applying person-level exclusions.
        other_income = add(person, period, p.sources.unearned, options=[ADD])
        rental_income = (
            max_(person("rental_income", period), 0)
            + max_(person("farm_rent_income", period), 0)
        ) * p.rental_income_rate
        # Rental inputs approximate reported gross rents; model data may
        # instead contain net rents. No new gross-rental input is introduced.
        household_income = spm_unit.sum(
            (earnings + other_income + rental_income) * counted_person
        )
        interest = spm_unit.sum(person("interest_income", period) * counted_person)
        countable_interest = max_(interest - p.interest_exclusion, 0)
        # RI Works is a household grant, counted once, not once per member.
        # There is no RI state SSI supplement variable in the current model.
        works = spm_unit("ri_works", period, options=[ADD])
        income = household_income + countable_interest + works
        # These reported amounts approximate verified court-ordered payments.
        dependent_expenses = add(spm_unit, period, p.dependent_expense_sources)
        childcare = spm_unit("childcare_expenses", period)
        subsidies = spm_unit("child_care_subsidies", period)
        childcare_deduction = where(subsidies == 0, childcare, 0)
        # Adult daycare/nursing-home attribution cannot be isolated reliably
        # from broader care inputs. Medicare deductions are user-deferred.
        return max_(income - dependent_expenses - childcare_deduction, 0)
