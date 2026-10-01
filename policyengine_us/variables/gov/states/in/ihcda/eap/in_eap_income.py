from policyengine_us.model_api import *


class in_eap_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Indiana EAP annual countable income"
    defined_for = StateCode.IN
    reference = "https://www.in.gov/ihcda/files/Indiana-LIHEAP-Intake-and-Operations-Program-Manual-PY2026.pdf#page=47,48,49,50,51,52,53,54,55,56,57,58,59,60,61"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states["in"].ihcda.eap
        person = spm_unit.members
        age = person("age", period)
        dependent = person("is_tax_unit_dependent", period)
        student = (
            person("is_in_secondary_school", period)
            | person("is_in_k12_school", period)
            | (
                person("is_full_time_college_student", period)
                & (age <= p.income.student_age_limit)
            )
        )
        counted = (age >= p.eligibility.adult_age) & ~(dependent & student)
        # Use annual inputs as an approximation to the annualized preceding three months.
        # Section 6.1 prefers paystub federal taxable gross when supplied; current wages
        # do not identify that paystub field. The manual asks for gross amounts:
        # Schedule C line 5, Schedule F line 9 and the Schedule E rent, partnership and
        # S corporation, estate and trust, and farm rental lines. The existing
        # self-employment, farm and rental inputs are net approximations of those
        # amounts: no new gross inputs or separate business/work-expense adjustments
        # are introduced in this project. Each source is floored at zero, so a loss in
        # one source cannot offset other counted income.
        other = 0
        for source in p.income.sources:
            other = other + max_(person(source, period), 0)
        other = other * counted
        # Child SSA benefits count despite the general under-18 exclusion. Only reported
        # Part B premiums are available to approximate the required net SSA payment;
        # Part D, withholding, overpayment recovery, and exact garnishment are unavailable.
        ssa = max_(
            person("social_security", period)
            - person("medicare_part_b_premiums_reported", period),
            0,
        )
        ssa = ssa + person("ssi", period)
        # Actual support paid is deductible. Child support received, TANF, capital gains,
        # tax refunds, and educational assistance are excluded. Recurring versus lump-sum
        # receipts, royalties, protected employment, and specific VA/insurance exclusions
        # cannot all be distinguished from existing inputs.
        support = max_(person("child_support_expense", period), 0)
        return max_(spm_unit.sum(other + ssa - support), 0)
