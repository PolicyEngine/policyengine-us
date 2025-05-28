from policyengine_us.model_api import *


class savers_credit_credit_limit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Retirement Savings Credit"
    unit = USD
    reference = (
        "https://www.irs.gov/pub/irs-pdf/f8880.pdf",
        "https://www.law.cornell.edu/uscode/text/26/25B#c",
    )

    def formula(tax_unit, period, parameters):
        income_tax_before_credits = tax_unit(
            "income_tax_before_credits", period
        )
        foreign_tax_credit = tax_unit("foreign_tax_credit", period)
        cdcc = tax_unit("cdcc", period)
        non_refundable_american_opportunity_credit = tax_unit(
            "non_refundable_american_opportunity_credit", period
        )
        lifetime_learning_credit = tax_unit("lifetime_learning_credit", period)
        return max_(
            income_tax_before_credits
            - foreign_tax_credit
            - cdcc
            - non_refundable_american_opportunity_credit
            - lifetime_learning_credit,
            0,
        )
