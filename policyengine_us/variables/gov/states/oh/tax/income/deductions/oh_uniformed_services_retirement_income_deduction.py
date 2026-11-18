from policyengine_us.model_api import *


class oh_uniformed_services_retirement_income_deduction(Variable):
    value_type = float
    entity = Person
    label = "Ohio uniformed services retirement income deduction"
    definition_period = YEAR
    unit = USD
    reference = (
        "https://codes.ohio.gov/ohio-revised-code/section-5747.01#A_23",
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/it1040-bundle.pdf#page=4",
    )
    defined_for = StateCode.OH

    def formula(person, period, parameters):
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        military_retirement = person("military_retirement_income", period)
        return is_head_or_spouse * military_retirement
