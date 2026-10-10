from policyengine_us.model_api import *
from policyengine_core.tracers import SimpleTracer


class tax_liability_if_not_itemizing(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax liability if not itemizing"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        simulation = tax_unit.simulation
        # The branch keeps this simulation's claim of right method (26 U.S.C.
        # 1341) rather than choosing its own, whatever is calculated first.
        claim_of_right_method = tax_unit("claim_of_right_credit_applies", period)
        non_itemized_branch = get_override_branch(
            simulation,
            "not_itemizing",
            period,
            {
                "tax_unit_itemizes": np.zeros((tax_unit.count,), dtype=bool),
                "claim_of_right_credit_applies": claim_of_right_method,
            },
        )
        return non_itemized_branch.calculate("income_tax", period)
