from policyengine_us.model_api import *


class id_liheap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Idaho LIHEAP countable annual income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ID
    reference = (
        # PDF pages 5-7
        "https://liheapch.acf.gov/docs/2026/state-plans/ID_Plan_2026.pdf#page=5"
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.id.dhw.liheap.income
        person = spm_unit.members
        # Annual flows approximate prior-month receipts. Source losses do not
        # offset other receipts; existing net business inputs need no deduction.
        earned = sum(
            max_(add(person, period, [source]), 0) for source in p.sources.earned
        )
        adult = person("age", period) >= p.earned_income_min_age
        unearned = sum(
            max_(add(person, period, [source]), 0) for source in p.sources.unearned
        )
        social_security = max_(
            person("social_security", period)
            - max_(person("medicare_part_b_premium", period), 0),
            0,
        )
        # Nonqualified members' income counts. Child support, VA and general
        # assistance remain excluded under the accepted plan's checklist.
        return spm_unit.sum(
            where(adult, earned, 0) + unearned + social_security
        ) + max_(spm_unit("tanf", period), 0)
