from policyengine_us.model_api import *


class snap_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    label = "SNAP earned income"
    documentation = "Earned income for calculating the SNAP earned income deduction"
    reference = (
        "https://www.law.cornell.edu/cfr/text/7/273.9#b_1",
        "https://www.law.cornell.edu/cfr/text/7/273.11#c",
    )
    unit = USD

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        employment = person("snap_earned_income_person", period)
        share = person("snap_income_counted_share", period)
        # Self-employment income net of the expense deduction is computed
        # at the SPM unit level; attribute it to members in proportion to
        # their gross self-employment income. Gross amounts are floored at
        # zero per enterprise, so the attribution ratio is bounded to
        # [0, 1]. Non-countable earners remain in the attribution base, so
        # their shares are dropped rather than reattributed to countable
        # earners. This mirrors the attribution in snap_gross_test_income,
        # which substitutes the full-count share.
        countable = person("snap_countable_earner", period)
        gross_self_employment = person(
            "snap_gross_self_employment_income_person", period
        )
        unit_gross = spm_unit.sum(gross_self_employment)
        unit_net = spm_unit(
            "snap_self_employment_income_after_expense_deduction", period
        )
        counted_weight = spm_unit.sum(gross_self_employment * countable * share)
        counted_self_employment = (
            unit_net * counted_weight / where(unit_gross > 0, unit_gross, 1)
        )
        return max_(spm_unit.sum(employment * share) + counted_self_employment, 0)
