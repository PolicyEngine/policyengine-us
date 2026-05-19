from policyengine_us.model_api import *


class ky_ktap_dependent_care_disregard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Kentucky K-TAP dependent care disregard"
    unit = USD
    definition_period = MONTH
    reference = "https://apps.legislature.ky.gov/law/kar/titles/921/002/016/"
    defined_for = StateCode.KY

    def formula(spm_unit, period, parameters):
        # NOTE: Full-time/part-time distinction not modeled.
        p = parameters(period).gov.states.ky.dcbs.ktap.income.deductions
        person = spm_unit.members
        is_dependent = person("is_tax_unit_dependent", period)
        age = person("age", period.this_year)
        max_per_child = p.dependent_care.calc(age) * is_dependent
        total_max_disregard = spm_unit.sum(max_per_child)
        childcare_expenses = spm_unit("childcare_expenses", period)
        return min_(childcare_expenses, total_max_disregard)
