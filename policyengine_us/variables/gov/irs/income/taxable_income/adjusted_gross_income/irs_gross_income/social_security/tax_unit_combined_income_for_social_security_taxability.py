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

        # The legislation directs the usage an income definition that is
        # a particularly modified AGI, plus half of gross Social Security
        # payments. We assume that the 'half' here is the same underlying
        # parameter as the lower taxability marginal rate (also 50% in the
        # baseline), and that they would be mechanically the same parameter.

        ss_fraction = p.rate.lower * gross_ss
        return tax_unit("taxable_ss_magi", period) + ss_fraction
