from policyengine_us.model_api import *


class tax_unit_railroad_social_security_equivalent_benefits_for_taxability(Variable):
    value_type = float
    entity = TaxUnit
    label = (
        "Tax unit Railroad Retirement social security equivalent benefits "
        "for taxability"
    )
    unit = USD
    documentation = (
        "Social security equivalent benefits of the head and spouse. As in "
        "tax_unit_social_security_for_taxability, a tax unit dependent's "
        "benefits are the dependent's own income."
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/86#d_1_B"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        total = tax_unit(
            "tax_unit_railroad_social_security_equivalent_benefits", period
        )
        is_dependent = person("is_tax_unit_dependent", period)
        benefits = person("railroad_social_security_equivalent_benefits", period)
        dependent_benefits = tax_unit.sum(is_dependent * benefits)
        return max_(0, total - dependent_benefits)
