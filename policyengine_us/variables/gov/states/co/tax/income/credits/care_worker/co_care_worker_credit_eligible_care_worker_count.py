from policyengine_us.model_api import *


class co_care_worker_credit_eligible_care_worker_count(Variable):
    value_type = float
    entity = TaxUnit
    label = "Number of eligible Care Workers for the Colorado Care Worker Tax Credit"
    defined_for = StateCode.CO
    definition_period = YEAR
    reference = "https://law.justia.com/codes/colorado/title-39/specific-taxes/income-tax/article-22/part-5/section-39-22-566/"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        care_worker = person(
            "co_care_worker_credit_eligible_care_worker", period
        )
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return tax_unit.sum(care_worker & head_or_spouse)
