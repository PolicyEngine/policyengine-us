from policyengine_us.model_api import *
from policyengine_us.variables.gov.aca.csr.marketplace_csr_category import (
    MarketplaceCSRCategory,
)


class marketplace_csr_actuarial_value(Variable):
    value_type = float
    entity = TaxUnit
    label = "Marketplace cost-sharing reduction actuarial value"
    unit = "/1"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/45/156.420#a"
    defined_for = "marketplace_csr_eligible"

    def formula(tax_unit, period, parameters):
        category = tax_unit("marketplace_csr_category", period)
        p = parameters(period).gov.aca.csr.actuarial_value
        return select(
            [
                category == MarketplaceCSRCategory.AV_94,
                category == MarketplaceCSRCategory.AV_87,
                category == MarketplaceCSRCategory.AV_73,
            ],
            [p.highest, p.middle, p.lowest],
        )
