from policyengine_us.model_api import *


class lifetime_learning_credit_credit_limit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Lifetime Learning Credit credit limit"
    unit = USD
    documentation = "Value of the non-refundable Lifetime Learning Credit"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/25A#c"

    def formula(tax_unit, period, parameters):
        income_tax_before_credits = tax_unit(
            "income_tax_before_credits", period
        )
        foreign_tax_credit = tax_unit("foreign_tax_credit", period)
        cdcc = tax_unit("cdcc", period)
        non_refundable_american_opportunity_credit = tax_unit(
            "non_refundable_american_opportunity_credit", period
        )
        return max_(
            income_tax_before_credits
            - foreign_tax_credit
            - cdcc
            - non_refundable_american_opportunity_credit,
            0,
        )
