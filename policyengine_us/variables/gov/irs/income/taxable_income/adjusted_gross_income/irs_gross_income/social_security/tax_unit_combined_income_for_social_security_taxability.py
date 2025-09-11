from policyengine_us.model_api import *


class tax_unit_combined_income_for_social_security_taxability(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Taxable Social Security combined income"
    unit = USD
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/86"
        "https://www.ssa.gov/benefits/retirement/planner/taxes.html"
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.social_security.taxability
        gross_ss = tax_unit("tax_unit_social_security", period)

        # The legislation directs the usage of an income definition that is
        # a particularly modified AGI, plus half of gross Social Security
        # payments. Per IRC Section 86(b)(1), this fraction is always 0.5
        # regardless of the taxation rates applied to the benefits.

        ss_fraction = p.combined_income_ss_fraction * gross_ss
        return tax_unit("taxable_ss_magi", period) + ss_fraction
