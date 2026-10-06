from policyengine_us.model_api import *

# The person-level business, rental and estate amounts whose losses
# limited_business_loss deducts.
BUSINESS_INCOME_SOURCES = [
    "total_self_employment_income",
    "farm_operations_income",
    "rental_income",
    "farm_rent_income",
    "estate_income",
    "partnership_s_corp_income",
]


class loss_ald_person(Variable):
    value_type = float
    entity = Person
    label = "Business and capital loss ALD for each person"
    unit = USD
    documentation = (
        "Each head's or spouse's part of the tax unit's business and capital "
        "loss deduction (loss_ald). The business loss after the Section 461(l) "
        "limit (limited_business_loss) is divided in proportion to each "
        "spouse's own business, farm, rental, estate and partnership losses; "
        "a Form 4797 loss, recorded only for the tax unit, counts equally for "
        "the head and spouse, as other_net_gain_gross_income counts the gain. "
        "The rest of loss_ald, the capital loss deduction, is divided in "
        "proportion to each spouse's own net capital losses. A tax unit "
        "dependent's losses are on their own return, so their part is zero."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/165",
        "https://www.law.cornell.edu/uscode/text/26/461#l",
        "https://www.law.cornell.edu/uscode/text/26/1211#b",
    )

    def formula(person, period, parameters):
        tax_unit = person.tax_unit
        business_loss = 0
        for source in BUSINESS_INCOME_SOURCES:
            business_loss = business_loss + max_(0, -person(source, period))
        other_net_loss = max_(0, -tax_unit("other_net_gain", period))
        equal_share = filer_share(person, period, 0 * other_net_loss)
        business_loss = business_loss + other_net_loss * equal_share
        business_share = filer_share(person, period, business_loss)
        capital_share = filer_share(person, period, person("capital_losses", period))
        limited_business_loss = tax_unit("limited_business_loss", period)
        capital_loss_deduction = tax_unit("loss_ald", period) - limited_business_loss
        return (
            limited_business_loss * business_share
            + capital_loss_deduction * capital_share
        )
