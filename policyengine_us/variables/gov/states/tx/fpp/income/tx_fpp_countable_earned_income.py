from policyengine_us.model_api import *


class tx_fpp_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Texas Family Planning Program countable earned income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/regulations/texas/1-Tex-Admin-Code-SS-382-109",
        "https://www.hhs.texas.gov/handbooks/family-planning-program-policy-manual/4100-client-eligibility-screening-process",
    )
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.tx.fpp.income
        person = spm_unit.members
        earned = add(person, period, p.sources.earned)
        # Per 1 TAC 382.109(3)(A), the earnings of a child are exempt;
        # Manual 4140 treats 18-year-olds as adults.
        is_adult = person("age", period) >= p.child_age_threshold
        return spm_unit.sum(where(is_adult, earned, 0))
