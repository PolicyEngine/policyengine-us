from policyengine_us.model_api import *


class MarketplaceCSRCategory(Enum):
    NONE = "None"
    AV_94 = "94 percent actuarial value"
    AV_87 = "87 percent actuarial value"
    AV_73 = "73 percent actuarial value"


class marketplace_csr_category(Variable):
    value_type = Enum
    possible_values = MarketplaceCSRCategory
    default_value = MarketplaceCSRCategory.NONE
    entity = TaxUnit
    label = "Marketplace cost-sharing reduction category"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/45/155.305#g_2"

    def formula(tax_unit, period, parameters):
        eligible = tax_unit("marketplace_csr_eligible", period)
        magi_fraction = tax_unit("aca_magi_fraction", period)
        p = parameters(period).gov.aca.csr.income_threshold
        return select(
            [
                eligible & (magi_fraction <= p.highest_av_maximum),
                eligible & (magi_fraction <= p.middle_av_maximum),
                eligible & (magi_fraction <= p.maximum),
            ],
            [
                MarketplaceCSRCategory.AV_94,
                MarketplaceCSRCategory.AV_87,
                MarketplaceCSRCategory.AV_73,
            ],
            default=MarketplaceCSRCategory.NONE,
        )
