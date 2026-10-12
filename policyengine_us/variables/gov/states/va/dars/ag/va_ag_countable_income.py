from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._apply_ssi_exclusions import (
    _apply_ssi_exclusions,
)


class va_ag_countable_income(Variable):
    value_type = float
    entity = Person
    label = "Virginia Auxiliary Grant countable income"
    definition_period = MONTH
    unit = USD
    reference = "https://townhall.virginia.gov/l/GetFile.cfm?File=C:%5CTownHall%5Cdocroot%5CGuidanceDocs%5C262%5CGDoc_DARS_5346_v2.pdf"

    def formula(person, period, parameters):
        joint = (
            person.marital_unit.sum(person("va_ag_is_joint_initial_month", period)) == 2
        )
        earned = max_(
            person("ssi_earned_income", period)
            - person("ssi_blind_or_disabled_working_student_exclusion", period),
            0,
        )
        unearned = max_(person("ssi_unearned_income", period), 0)
        earned = where(joint, person.marital_unit.sum(earned), earned)
        unearned = where(joint, person.marital_unit.sum(unearned), unearned)
        non_ssi_countable = (
            _apply_ssi_exclusions(
                earned * MONTHS_IN_YEAR, unearned * MONTHS_IN_YEAR, parameters, period
            )
            / MONTHS_IN_YEAR
        )
        non_ssi_countable = where(joint, non_ssi_countable / 2, non_ssi_countable)
        ssi = person("ssi", period)
        # Chapter D uses SSA's verified net income for current SSI recipients;
        # non-SSI institutional recipients have individual income budgets.
        countable = where(
            ssi > 0, person("ssi_countable_income", period) + ssi, non_ssi_countable
        )
        exclusions = max_(person("va_ag_allowable_income_exclusions", period), 0)
        return max_(countable - exclusions, 0)
