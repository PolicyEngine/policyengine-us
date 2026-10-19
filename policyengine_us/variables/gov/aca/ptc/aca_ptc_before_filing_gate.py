from policyengine_us.model_api import *


class aca_ptc_before_filing_gate(Variable):
    value_type = float
    entity = TaxUnit
    label = "ACA premium tax credit before the filing condition"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/36B#b"
    documentation = (
        "The premium tax credit the tax unit could claim on a return: the "
        "benchmark premium less the required contribution. aca_ptc is this "
        "amount for a tax unit that files a return claiming it."
    )
    defined_for = "is_aca_ptc_eligible"

    def formula(tax_unit, period, parameters):
        return 0

    def formula_2018(tax_unit, period, parameters):
        # The benchmark for the coverage family (26 CFR 1.36B-3(f)), which
        # leaves out an enrollee who can be claimed on another return.
        plan_cost = tax_unit("aca_ptc_slcsp", period)
        income = tax_unit("aca_magi", period)
        applicable_figure = tax_unit("aca_required_contribution_percentage", period)
        return max_(0, plan_cost - income * applicable_figure)
