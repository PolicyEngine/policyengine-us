from policyengine_us.model_api import *


class co_care_worker_credit_eligible_care_worker(Variable):
    value_type = bool
    entity = Person
    label = "Eligible Care Worker for the Colorado Care Worker Tax Credit"
    defined_for = StateCode.CO
    definition_period = YEAR
    reference = "https://law.justia.com/codes/colorado/title-39/specific-taxes/income-tax/article-22/part-5/section-39-22-566/"
