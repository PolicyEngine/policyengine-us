from policyengine_us.model_api import *
from policyengine_us.variables.gov.irs.income.taxable_income.adjusted_gross_income.irs_gross_income.social_security.taxable_social_security import (
    allocate_to_head_and_spouse,
)


class taxable_railroad_social_security_equivalent_benefits(Variable):
    value_type = float
    entity = Person
    label = "Taxable Railroad Retirement social security equivalent benefits"
    unit = USD
    documentation = (
        "The head's or spouse's tier 1 railroad retirement benefits included "
        "in gross income under IRC 86, allocated in proportion to their social "
        "security equivalent benefits as taxable_social_security allocates "
        "title II benefits. 45 U.S.C. 231m(a) bars states from taxing them."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/86#d_1_B",
        "https://www.law.cornell.edu/uscode/text/45/231m#a",
    )

    def formula(person, period, parameters):
        unit_taxable = person.tax_unit(
            "tax_unit_taxable_railroad_social_security_equivalent_benefits", period
        )
        benefits = person("railroad_social_security_equivalent_benefits", period)
        unit_benefits = person.tax_unit(
            "tax_unit_railroad_social_security_equivalent_benefits_for_taxability",
            period,
        )
        return allocate_to_head_and_spouse(
            person, period, unit_taxable, benefits, unit_benefits
        )
