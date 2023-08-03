from policyengine_us.model_api import *


class oh_uniformed_services_retirement_income_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "OH Uniformed services retirement income"
    definition_period = YEAR
    unit = USD
    reference = "https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/it1040-bundle.pdf#page=4"
