from policyengine_us.model_api import *


class ky_ktap_countable_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Kentucky K-TAP countable unearned income"
    unit = USD
    definition_period = MONTH
    reference = "https://apps.legislature.ky.gov/law/kar/titles/921/002/016/"
    defined_for = StateCode.KY

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ky.dcbs.ktap.income.deductions
        gross_unearned = add(spm_unit, period, ["tanf_gross_unearned_income"])
        child_support = add(spm_unit, period, ["child_support_received"])
        child_support_exclusion = min_(
            child_support, p.child_support_disregard
        )
        return max_(gross_unearned - child_support_exclusion, 0)
