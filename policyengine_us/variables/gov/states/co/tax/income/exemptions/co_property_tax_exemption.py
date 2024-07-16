from policyengine_us.model_api import *


class co_property_tax_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado property tax exemption"
    unit = USD
    definition_period = YEAR
    reference = "https://casetext.com/statute/colorado-revised-statutes/title-39-taxation/property-tax/exemptions/article-3-exemptions/part-2-property-tax-exemption-for-qualifying-seniors-and-disabled-veterans/section-39-3-203-property-tax-exemption-qualifications"
    defined_for = StateCode.CO
