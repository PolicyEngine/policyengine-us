from policyengine_us.model_api import *


class tax_unit_social_security(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax unit Social Security"
    unit = USD
    definition_period = YEAR
    reference = "https://www.irs.gov/faqs/social-security-income"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        not_dependent = ~person("is_tax_unit_dependent", period)
        social_security = person("social_security", period)
        return tax_unit.sum(not_dependent * social_security)
