from policyengine_us.model_api import *


class aca_ptc(Variable):
    value_type = float
    entity = TaxUnit
    label = "ACA premium tax credit for tax unit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/36B"
    defined_for = "is_aca_ptc_eligible"

    def formula(tax_unit, period, parameters):
        return 0

    def formula_2024(tax_unit, period, parameters):
        plan_cost = tax_unit("slcsp", period)
        income = tax_unit("aca_magi", period)
        applicable_figure = tax_unit("aca_required_contribution_percentage", period)
        # IRC § 36B(a) conditions the PTC on filing a return (Form 8962).
        # Gate on tax_unit_is_filer so non-filers receive $0.
        is_filer = tax_unit("tax_unit_is_filer", period)
        return max_(0, plan_cost - income * applicable_figure) * is_filer
