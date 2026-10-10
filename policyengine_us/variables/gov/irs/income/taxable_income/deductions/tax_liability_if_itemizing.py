from policyengine_us.model_api import *


class tax_liability_if_itemizing(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax liability if itemizing"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        simulation = tax_unit.simulation
        # Settle the claim of right method (26 U.S.C. 1341) in this simulation
        # first, so that the branch uses it and does not choose its own.
        tax_unit("claim_of_right_credit_applies", period)
        itemized_branch = get_override_branch(
            simulation,
            "itemizing",
            period,
            {"tax_unit_itemizes": np.ones((tax_unit.count,), dtype=bool)},
        )
        return itemized_branch.calculate("income_tax", period)
