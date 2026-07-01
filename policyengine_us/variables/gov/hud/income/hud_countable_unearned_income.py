from policyengine_us.model_api import *


class hud_countable_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "HUD countable unearned income"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/24/5.609"

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        # Foster children and adults are not family members (24 CFR 5.603), so
        # their own income does not count.
        is_family_member = ~person("is_in_foster_care", period)
        unearned_income = spm_unit.sum(
            person("hud_unearned_income", period) * is_family_member
        )
        # TANF is a family benefit assigned to the unit, not an individual, so
        # it is counted whole and is not subject to the foster-member mask.
        return unearned_income + spm_unit("tanf", period)
