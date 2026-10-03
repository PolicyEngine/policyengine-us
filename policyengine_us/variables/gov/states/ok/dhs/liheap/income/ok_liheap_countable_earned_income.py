from policyengine_us.model_api import *


class ok_liheap_countable_earned_income(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = USD
    label = "Oklahoma LIHEAP gross countable earned income"
    defined_for = StateCode.OK
    reference = (
        # OAC 340:20-1-11(a)-(b), PDF pages 576-578, effective September 15, 2025.
        "https://oklahoma.gov/content/dam/ok/en/omma/content/rulemaking-process/rules/Register_Volume-42_Issue-20.pdf#page=576",
        "https://www.law.cornell.edu/regulations/oklahoma/OAC-340-50-7-22",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ok.dhs.liheap.income
        income = 0
        for source in p.sources.earned:
            income = income + max_(person(source, period), 0)
        # Existing net business inputs replace gross receipts; do not apply
        # an additional 50% business deduction or introduce work expenses.
        # K-12 attendance defaults to an overridable age-based imputation.
        # Tax dependency approximates parental control; exact control
        # relationships and federal student-work programs are not modeled.
        exempt_student = (
            (person("age", period) < p.student_earned_income_age_limit)
            & person("is_in_k12_school", period)
            & person("is_tax_unit_dependent", period)
        )
        return where(exempt_student, 0, income)
