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
    defined_for = StateCode.OH
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
        # NOTE: PolicyEngine's federal SSI still counts interest and dividends
        # (#10079), so for an SSI recipient with that income the SSI counted
        # here is understated and RSS is overstated by the same amount.
        # NOTE: SSI's joint-claim test reads only aged, blind or disabled
        # status, so a spouse who declines SSI is still budgeted jointly
        # (#10138).
        federal_ssi = person("ssi", period)
        federal_ssi = where(couple, person.marital_unit.sum(federal_ssi), federal_ssi)
        # Ohio applies the same $20 general, $65 earned and one-half earned
        # income exclusions (5160:1-3-03.2(D)(2)(l), (E)(5), (E)(7)), so the SSI
        # exclusion parameters are used and an SSI reform carries over to RSS.
        # They apply once per couple. SSI is needs-based income and does not
        # receive the general $20 disregard (D)(2)(l).
        countable = (
            _apply_ssi_exclusions(
                earned * MONTHS_IN_YEAR, unearned * MONTHS_IN_YEAR, parameters, period
            )
            / MONTHS_IN_YEAR
            + federal_ssi
        )
        # NOTE: 5160:1-5-01(E)(2) determines a couple's eligibility
        # "collectively, utilizing the appropriate couple income standard as
        # defined in rule 5160:1-3-03.5", and 5160:1-3-03.5(B)(2) defines that
        # standard as "the current supplemental security income (SSI) benefit
        # rate for a couple". Read literally, a couple whose only income is SSI
        # would be at that standard and ineligible under (E)(4)(b). Ohio
        # publishes only the RSS income standard of 5160:1-5-01(B)(2), so the
        # model compares pooled countable income with twice the RSS income
        # standard, which pays each spouse the RSS income standard less half
        # the pooled income.
        return where(couple, countable / 2, countable)
