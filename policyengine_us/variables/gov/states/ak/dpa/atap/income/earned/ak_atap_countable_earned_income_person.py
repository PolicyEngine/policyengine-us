from policyengine_us.model_api import *


class ak_atap_countable_earned_income_person(Variable):
    value_type = float
    entity = Person
    label = "Alaska ATAP countable earned income per person"
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/alaska/7-AAC-45.480"
    defined_for = StateCode.AK

    def formula(person, period, parameters):
        # Per 7 AAC 45.480: Deductions depend on applicant status
        # (a)(1) New applicants: $90 flat deduction
        # (a)(2) + (b) Continuing recipients: $150 flat + percentage
        p = parameters(period).gov.states.ak.dpa.atap.income
        gross_earned = person("tanf_gross_earned_income", period)
        is_enrolled = person.spm_unit("is_tanf_enrolled", period)

        # New applicants: $90 flat deduction only
        new_applicant_countable = max_(
            gross_earned - p.deductions.initial_work_deduction, 0
        )

        # Continuing recipients: $150 flat + percentage of remainder
        # NOTE: Alaska uses tiered deductions based on months receiving assistance:
        #   Tier 1 (months 1-12): $150 + 33%
        #   Tier 2 (months 13-24): $150 + 25%
        #   Tier 3 (months 25-36): $150 + 20%
        #   Tier 4 (months 37-48): $150 + 15%
        #   Tier 5 (months 49-60): $150 + 10%
        #   Beyond 60 months: $150 only (0%)
        #   Only Tier 1 is modeled.
        after_flat = max_(gross_earned - p.work_incentive.flat, 0)
        percent_disregard = after_flat * p.work_incentive.rate
        continuing_countable = max_(
            gross_earned - p.work_incentive.flat - percent_disregard, 0
        )

        return where(
            is_enrolled, continuing_countable, new_applicant_countable
        )
