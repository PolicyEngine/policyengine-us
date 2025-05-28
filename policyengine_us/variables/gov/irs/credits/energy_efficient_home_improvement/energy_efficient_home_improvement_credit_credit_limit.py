from policyengine_us.model_api import *


class energy_efficient_home_improvement_credit_credit_limit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Energy efficient home improvement credit credit limit"
    documentation = "Residential clean energy credit"
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/25C"

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
        savers_credit = tax_unit("savers_credit", period)
        residential_clean_energy_credit = tax_unit(
            "residential_clean_energy_credit", period
        )
        return max_(
            income_tax_before_credits
            - foreign_tax_credit
            - cdcc
            - non_refundable_american_opportunity_credit
            - lifetime_learning_credit
            - savers_credit
            - residential_clean_energy_credit,
            0,
        )
