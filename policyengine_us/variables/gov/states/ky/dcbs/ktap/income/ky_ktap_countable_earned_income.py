from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.ky.dcbs.ktap.income.ky_ktap_earned_income_helpers import (
    ky_ktap_countable_earnings,
)


class ky_ktap_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Kentucky K-TAP countable earned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://apps.legislature.ky.gov/law/kar/titles/921/002/016/",
        "https://apps.legislature.ky.gov/law/kar/titles/921/002/016/10142/",
    )
    defined_for = StateCode.KY

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ky.dcbs.ktap.income.deductions
        person = spm_unit.members
        gross_earned = person("tanf_gross_earned_income", period)
        dep_care = person("ky_ktap_dependent_care_disregard_person", period)
        countable = ky_ktap_countable_earnings(gross_earned, dep_care, p, period)
        return spm_unit.sum(countable)
