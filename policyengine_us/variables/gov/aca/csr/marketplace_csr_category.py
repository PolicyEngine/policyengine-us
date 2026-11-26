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
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/18071#c_2",
        "https://www.law.cornell.edu/cfr/text/45/155.305#g_2",
    )

    def formula(tax_unit, period, parameters):
        eligible = tax_unit("marketplace_csr_eligible", period)
        # 42 U.S.C. 18071(c)(2) and 45 CFR 155.305(g)(2) set each tier by
        # household income "not more than" (the regulation: "less than or equal
        # to") 150, 200 and 250 percent of the poverty line. Test the exact
        # ratio, not the truncated aca_magi_fraction: truncation maps
        # 150.00%-150.99% to 1.50, which would put incomes above 150% in the
        # 94% tier.
        magi = max_(tax_unit("aca_magi", period), 0)
        magi_fraction = magi / tax_unit("tax_unit_fpg", period.last_year)
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
