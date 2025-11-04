from policyengine_us.model_api import *


class pa_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Pennsylvania TANF eligibility"
    definition_period = MONTH
    defined_for = StateCode.PA
    reference = "55 Pa. Code Chapters 105, 183 - TANF Eligibility Requirements"
    documentation = "Meets all Pennsylvania TANF eligibility requirements: categorical (has minor child or pregnant woman), resource limit, and income limit. https://www.pacodeandbulletin.gov/Display/pacode?titleNumber=055&file=/secure/pacode/data/055/055toc.html"

    def formula(spm_unit, period, parameters):
        # Must meet all three eligibility criteria
        categorical = spm_unit("pa_tanf_categorical_eligible", period)
        resources = spm_unit("pa_tanf_resources_eligible", period)
        income = spm_unit("pa_tanf_income_eligible", period)

        return categorical & resources & income
