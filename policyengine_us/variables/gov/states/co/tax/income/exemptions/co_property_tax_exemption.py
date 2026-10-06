from policyengine_us.model_api import *


class co_property_tax_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado property tax exemption"
    unit = USD
    definition_period = YEAR
    reference = "https://law.justia.com/codes/colorado/title-39/property-tax/exemptions/article-3/part-2/section-39-3-203/"
    defined_for = StateCode.CO
