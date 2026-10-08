from policyengine_us.model_api import *


class ri_liheap_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Rhode Island LIHEAP countable income"
    defined_for = StateCode.RI
    reference = (
        # Manual sections III.E-H
        # PDF pages 14-21
        "https://ripuc.ri.gov/eventsactions/docket/4290-DHS-DR-PUC%203-6%20attachment%20LIHEAP%20Manual%202020%20-%20Final.pdf#page=14",
        # Plan sections 1.8-1.9
        # PDF pages 5-7
        "https://liheapch.acf.gov/docs/2026/state-plans/RI_Plan_2026.pdf#page=5",
        "https://dhs.ri.gov/media/9671/download?language=en",
        "https://dhs.ri.gov/media/9701/download?language=en",
        "https://westbaycap.org/wp-content/uploads/2025/08/Appendix-H-Application-Instructions-FY-26.pdf#page=2",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ri.dhs.liheap.income
        person = spm_unit.members
        age = person("age", period)
        # The FY2026 (Appendix H) and FY2027 application instructions (p2)
        # exclude the income of every full-time student aged 18-23. The 2020
        # manual (III.G p20) excluded only a child who was not the household
        # head; the current instructions govern.
        exempt_student = (age < p.student_age_limit) & person(
            "is_full_time_student", period
        )
        counted_person = (age >= p.minimum_income_age) & ~exempt_student
        # Existing net business receipts approximate the gross-receipts rule.
        # No additional 40% business deduction or new expense input is used.
        # Each source is floored at zero, so a loss in one source cannot
        # offset another.
        earnings = 0
        for source in p.sources.earned:
            earnings = earnings + max_(person(source, period), 0)
        other_income = 0
        for source in p.sources.unearned:
            other_income = other_income + max_(person(source, period), 0)
        rental_income = (
            max_(person("rental_income", period), 0)
            + max_(person("farm_rent_income", period), 0)
        ) * p.rental_income_rate
        # Rental inputs approximate reported gross rents; model data may
        # instead contain net rents. No new gross-rental input is introduced.
        household_income = spm_unit.sum(
            (earnings + other_income + rental_income) * counted_person
        )
        interest = spm_unit.sum(
            max_(person("interest_income", period), 0) * counted_person
        )
        countable_interest = max_(interest - p.interest_exclusion, 0)
        # The annual tanf aggregate includes ri_works and applies take-up;
        # ri_works alone is the entitlement a nonrecipient could get. The
        # household grant is counted once, not once per member.
        tanf = spm_unit("tanf", period)
        income = household_income + countable_interest + tanf
        deductions = add(spm_unit, period, p.deduction_sources)
        childcare = spm_unit("childcare_expenses", period)
        subsidies = spm_unit("child_care_subsidies", period)
        childcare_deduction = where(subsidies == 0, childcare, 0)
        # Adult daycare/nursing-home attribution cannot be isolated reliably
        # from broader care inputs, and Medicare prescription costs have no
        # input.
        return max_(income - deductions - childcare_deduction, 0)
