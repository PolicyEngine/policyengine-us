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
        "https://liheapch.acf.gov/docs/2026/state-plans/ID_Plan_2026.pdf#page=5",
        # IDAPA 16.04.14.010.06 and 151.02. PDF pages 3, 5
        "https://web.archive.org/web/20250910171431id_/https://adminrules.idaho.gov/rules/current/16/160414.pdf#page=3",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.id.dhw.liheap.income
        person = spm_unit.members
        # Annual flows approximate prior-month receipts. Source losses do not
        # offset other receipts; existing net business inputs need no deduction.
        earned = 0
        for source in p.sources.earned:
            earned = earned + max_(add(person, period, [source]), 0)
        unearned = 0
        for source in p.sources.unearned:
            unearned = unearned + max_(add(person, period, [source]), 0)
        social_security = max_(
            person("social_security", period)
            - person("medicare_part_b_premium", period),
            0,
        )
        # Every member's income counts, nonqualified members' and minors' included.
        # IDAPA 16.04.14.151.02.t leaves out child support, which is in neither list.
        return spm_unit.sum(earned + unearned + social_security) + spm_unit(
            "tanf", period
        )
