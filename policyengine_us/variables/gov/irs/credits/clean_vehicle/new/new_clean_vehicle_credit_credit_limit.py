from policyengine_us.model_api import *


class new_clean_vehicle_credit_credit_limit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "New clean vehicle credit credit limit"
    documentation = (
        "Nonrefundable credit for the purchase of a new clean vehicle"
    )
    unit = USD
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/30D",
        "https://www.democrats.senate.gov/imo/media/doc/inflation_reduction_act_of_2022.pdf#page=373",
    )
    defined_for = "new_clean_vehicle_credit_eligible"

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
        energy_efficient_home_improvement_credit = tax_unit(
            "energy_efficient_home_improvement_credit", period
        )
        elderly_disabled_credit = tax_unit("elderly_disabled_credit", period)
        return max_(
            income_tax_before_credits
            - foreign_tax_credit
            - cdcc
            - non_refundable_american_opportunity_credit
            - lifetime_learning_credit
            - savers_credit
            - residential_clean_energy_credit
            - energy_efficient_home_improvement_credit
            - elderly_disabled_credit,
            0,
        )
