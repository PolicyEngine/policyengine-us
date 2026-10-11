from policyengine_us.model_api import *


class tax_liability_if_itemizing(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax liability if itemizing"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        simulation = tax_unit.simulation
        overrides = {"tax_unit_itemizes": np.ones((tax_unit.count,), dtype=bool)}
        if tax_unit("claim_of_right_section_1341_eligible", period).any():
            # Keep this simulation's claim of right method (26 U.S.C. 1341)
            # rather than letting the branch choose its own. With no
            # qualifying repayment the method is false everywhere, and
            # leaving it out keeps the branch sharing this simulation's cache.
            overrides["claim_of_right_credit_applies"] = tax_unit(
                "claim_of_right_credit_applies", period
            )
        itemized_branch = get_override_branch(
            simulation,
            "itemizing",
            period,
            overrides,
        )
        return itemized_branch.calculate("income_tax", period)
