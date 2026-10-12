from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._apply_ssi_exclusions import (
    _apply_ssi_exclusions,
)


class oh_rss_countable_income(Variable):
    value_type = float
    entity = Person
    label = "Ohio RSS countable income"
    definition_period = MONTH
    unit = USD
    reference = (
        "https://codes.ohio.gov/ohio-administrative-code/rule-5160:1-5-01",
        "https://codes.ohio.gov/ohio-administrative-code/rule-5160:1-3-03.2",
    )

    def formula(person, period, parameters):
        # RSS does not deem income from an ineligible spouse or parent.
        eligible = person("oh_rss_eligible", period)
        couple = person.marital_unit.sum(eligible) == 2
        earned = max_(
            person("ssi_earned_income", period)
            - person("ssi_blind_or_disabled_working_student_exclusion", period),
            0,
        )
        # Interest and dividends are excluded under 5160:1-3-03.2(D)(2)(v).
        unearned = max_(
            person("ssi_unearned_income", period)
            - person("interest_income", period)
            - person("dividend_income", period),
            0,
        )
        earned = where(couple, person.marital_unit.sum(earned), earned)
        unearned = where(couple, person.marital_unit.sum(unearned), unearned)
        federal_ssi = person("ssi", period)
        federal_ssi = where(couple, person.marital_unit.sum(federal_ssi), federal_ssi)
        # Apply exclusions once per couple. SSI is needs-based income and does
        # not receive the general $20 disregard (D)(2)(l).
        countable = (
            _apply_ssi_exclusions(
                earned * MONTHS_IN_YEAR, unearned * MONTHS_IN_YEAR, parameters, period
            )
            / MONTHS_IN_YEAR
            + federal_ssi
        )
        return where(couple, countable / 2, countable)
