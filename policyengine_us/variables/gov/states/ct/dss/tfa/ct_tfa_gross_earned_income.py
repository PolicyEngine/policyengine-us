"""
Connecticut TFA gross earned income calculation.
"""

from policyengine_us.model_api import *


class ct_tfa_gross_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Connecticut TFA gross earned income"
    definition_period = MONTH
    defined_for = StateCode.CT
    unit = USD
    documentation = (
        "Total gross earned income for the Connecticut TFA assistance unit, "
        "including wages, salaries, self-employment income, and other earnings "
        "before any disregards or deductions are applied."
    )
    reference = (
        "Connecticut TANF State Plan 2024-2026, Income Treatment Section; "
        "Connecticut DSS Uniform Policy Manual Section 8030"
    )

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        p = parameters(period).gov.states.ct.dss.tfa

        # Get earned income for all household members
        employment_income = person("employment_income", period)
        self_employment_income = person("self_employment_income", period)

        # Total earned income per person
        total_earned = employment_income + self_employment_income

        # Student income disregard
        is_student = person("is_full_time_student", period.this_year)
        age = person("age", period.this_year)
        max_student_age = p.age_limits.max_age
        is_student_child = is_student & (age < max_student_age)

        # Apply full disregard for student income per CGS 17b-80
        student_disregard_rate = p.income_disregards.student_income_disregard
        countable_earned = where(
            is_student_child,
            total_earned * (1 - student_disregard_rate),
            total_earned,
        )

        # Sum across household
        return spm_unit.sum(countable_earned)
