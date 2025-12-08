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
        # Per 921 KAR 2:016 Section 5(3)(b):
        # Dependent care disregard caps:
        # - $200/month for child under age 2
        # - $175/month for child age 2-12 (full-time)
        # - $150/month for child age 2-12 (part-time)
        # - $0 for age 13+
        # Note: Full-time/part-time distinction (30 hrs/week threshold)
        # is not currently modeled; using full-time rate ($175).
        p = parameters(period).gov.states.ky.dcbs.ktap.income.deductions
        person = spm_unit.members
        age = person("age", period.this_year)
        max_per_child = p.dependent_care.calc(age)
        total_max_disregard = spm_unit.sum(max_per_child)
        childcare_expenses = spm_unit("childcare_expenses", period)
        return min_(childcare_expenses, total_max_disregard)
