from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.ky.dcbs.ktap.income.ky_ktap_earned_income_helpers import (
    ky_ktap_countable_earnings,
    ky_ktap_dependent_care_share,
)


class ky_ktap_ineligible_without_child_care_disregard(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Kentucky K-TAP case is ineligible without the child care disregard"
    definition_period = MONTH
    reference = (
        "https://apps.legislature.ky.gov/law/kar/titles/921/002/016/",
        "https://www.chfs.ky.gov/agencies/dcbs/dfs/Documents/OMVOLIII.pdf",
    )
    defined_for = StateCode.KY

    def formula(spm_unit, period, parameters):
        # Per MS 2810 B, a case whose countable income equals or exceeds the
        # standard of need is ineligible. Compute countable income with the
        # dependent care disregard for incapacitated adults only.
        p = parameters(period).gov.states.ky.dcbs.ktap.income.deductions
        person = spm_unit.members
        gross_earned = person("tanf_gross_earned_income", period)
        adult_care = spm_unit("ky_ktap_incapacitated_adult_care_disregard", period)
        adult_care_person = spm_unit.project(adult_care) * ky_ktap_dependent_care_share(
            person, period
        )
        countable_earned = spm_unit.sum(
            ky_ktap_countable_earnings(gross_earned, adult_care_person, p, period)
        )
        countable_unearned = spm_unit("ky_ktap_countable_unearned_income", period)
        standard_of_need = spm_unit("ky_ktap_standard_of_need", period)
        return countable_earned + countable_unearned >= standard_of_need
