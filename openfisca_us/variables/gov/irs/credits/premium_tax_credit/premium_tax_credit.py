from openfisca_us.model_api import *


class premium_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Premium Tax Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/36B"

    def formula(tax_unit, period, parameters):
        applicable_percentage = tax_unit("ptc_phase_out_rate", period)
        eligible = tax_unit("is_ptc_eligible", period)
        plan_cost = tax_unit("second_lowest_silver_plan_cost", period)
        income = tax_unit("medicaid_income", period)
        return eligible * max_(0, plan_cost - income * applicable_percentage)
