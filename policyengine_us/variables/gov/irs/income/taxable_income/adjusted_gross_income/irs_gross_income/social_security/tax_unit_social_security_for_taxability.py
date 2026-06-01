from policyengine_us.model_api import *


class tax_unit_social_security_for_taxability(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax unit Social Security for taxability"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/86",
        "https://www.irs.gov/faqs/social-security-income",
    )

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        total_social_security = tax_unit("tax_unit_social_security", period)
        not_dependent = ~person("is_tax_unit_dependent", period)
        social_security = person("social_security", period)
        dependent_social_security = tax_unit.sum(~not_dependent * social_security)
        return max_(0, total_social_security - dependent_social_security)
