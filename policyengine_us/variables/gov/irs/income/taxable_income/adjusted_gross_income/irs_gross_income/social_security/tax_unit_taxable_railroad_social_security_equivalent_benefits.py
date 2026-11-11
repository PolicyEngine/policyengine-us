from policyengine_us.model_api import *
from policyengine_us.variables.gov.irs.income.taxable_income.adjusted_gross_income.irs_gross_income.social_security.tax_unit_taxable_social_security import (
    section_86_share,
)


class tax_unit_taxable_railroad_social_security_equivalent_benefits(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Taxable Railroad Retirement social security equivalent benefits"
    documentation = (
        "Tier 1 railroad retirement benefits included in AGI: the share of "
        "tax_unit_taxable_section_86_benefits that the head's and spouse's "
        "social security equivalent benefits make up. It is figured from the "
        "benefits, not as the total less taxable title II benefits, so a "
        "change to tax_unit_taxable_social_security leaves it alone."
    )
    unit = USD
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/86#d_1_B",
        "https://www.law.cornell.edu/uscode/text/26/86#d_4",
    )

    def formula(tax_unit, period, parameters):
        taxable = tax_unit("tax_unit_taxable_section_86_benefits", period)
        share = section_86_share(
            tax_unit,
            period,
            "tax_unit_railroad_social_security_equivalent_benefits_for_taxability",
        )
        return taxable * share
