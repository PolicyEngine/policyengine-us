from policyengine_us.model_api import *


class nj_total_income(Variable):
    value_type = float
    entity = Person
    label = "New Jersey total income"
    unit = USD
    documentation = "New Jersey total income calculated as gross income plus additions minus subtractions per NJ Statute 54A:5-1. This is the income base before exclusions."
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/new-jersey/title-54a/section-54a-5-1/",
        "https://www.nj.gov/treasury/taxation/pdf/current/1040.pdf",
    )
    defined_for = StateCode.NJ

    def formula(person, period, parameters):
        # NJ Total Income = Gross Income + Additions - Subtractions
        # Per NJ Statute 54A:5-1 and Form NJ-1040
        gross_income = person("nj_gross_income", period)
        additions = person("nj_additions", period)
        subtractions = person("nj_agi_subtractions", period)
        return max_(0, gross_income + additions - subtractions)
