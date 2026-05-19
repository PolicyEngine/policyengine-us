from policyengine_us.model_api import *


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
        # (a) Work expense per person per MS 2840.A
        after_work_expense = max_(gross_earned - p.work_expense, 0)
        # (b) Dependent care per MS 2840.B
        dep_care = person("ky_ktap_dependent_care_disregard_person", period)
        after_dep_care = max_(after_work_expense - dep_care, 0)
        # (e) Time-limited EID per person per MS 2857
        # Uses calendar month as proxy for participation months.
        month = period.start.month
        eid_rate = p.earned_income_disregard_rate.calc(month)
        if p.earned_income_flat_disregard_in_effect:
            flat = p.earned_income_flat_disregard
            remainder = max_(after_dep_care - flat, 0)
            disregard = flat + eid_rate * remainder
        else:
            disregard = eid_rate * after_dep_care
        countable_per_person = max_(after_dep_care - disregard, 0)
        return spm_unit.sum(countable_per_person)
