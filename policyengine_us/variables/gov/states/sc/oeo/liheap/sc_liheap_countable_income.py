from policyengine_us.model_api import *


class sc_liheap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "South Carolina LIHEAP annual countable income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.SC
    reference = (
        "https://oeo.sc.gov/managedsites/prd/oeo/documents/2026%20LIHEAP%20State%20Plan.pdf#page=5,6",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.sc.oeo.liheap.income
        person = spm_unit.members
        # Existing net business inputs approximate self-employment receipts
        # without a second expense deduction. Annual flows approximate 30 days.
        earned = sum(max_(person(source, period), 0) for source in p.earned_sources)
        adult = person("age", period) >= p.earned_min_age
        unearned = add(person, period, p.unearned_sources)
        # The plan excludes minor earnings, not their unearned income. Adult-only
        # verification requirements are not a general minor-income exclusion.
        # Missing legal-settlement and earmarking facts are documented in README.
        return max_(spm_unit.sum(where(adult, earned, 0) + unearned), 0)
