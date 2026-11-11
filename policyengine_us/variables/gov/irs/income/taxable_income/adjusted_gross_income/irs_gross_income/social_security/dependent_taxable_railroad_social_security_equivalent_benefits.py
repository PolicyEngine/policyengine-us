from policyengine_us.model_api import *
from policyengine_us.variables.gov.irs.income.taxable_income.adjusted_gross_income.irs_gross_income.social_security.dependent_taxable_social_security import (
    dependent_taxable_section_86_share,
)


class dependent_taxable_railroad_social_security_equivalent_benefits(Variable):
    value_type = float
    entity = Person
    label = (
        "Dependent's taxable Railroad Retirement social security equivalent benefits"
    )
    unit = USD
    documentation = (
        "The tier 1 railroad retirement share of the social security benefits "
        "a dependent includes in gross income under IRC 86, figured on the "
        "dependent's own return as in dependent_taxable_social_security."
    )
    definition_period = YEAR
    defined_for = "is_tax_unit_dependent"
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/86#d_1_B",
        "https://www.law.cornell.edu/uscode/text/26/152#b_2",
    )

    def formula(person, period, parameters):
        return dependent_taxable_section_86_share(
            person, period, parameters, title_ii=False
        )
