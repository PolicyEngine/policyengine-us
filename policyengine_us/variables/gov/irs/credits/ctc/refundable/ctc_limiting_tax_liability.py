from policyengine_us.model_api import *


class ctc_limiting_tax_liability(Variable):
    value_type = float
    entity = TaxUnit
    label = "CTC-limiting tax liability"
    unit = USD
    documentation = "The tax liability used to determine the maximum amount of the non-refundable CTC. Excludes SALT from all calculations (this is an inaccuracy required to avoid circular dependencies)."
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        simulation = tax_unit.simulation
        no_salt_branch = simulation.get_branch("no_salt")
        no_salt_branch.set_input("salt_deduction", period, np.zeros(tax_unit.count))
        # Propagate the parent's itemization determination so the
        # no_salt branch doesn't re-enter
        # `tax_unit_itemizes` -> `tax_liability_if_itemizing` ->
        # `income_tax` -> `refundable_ctc`, which forms a cycle
        # (issue #8059). The parent's value has already been computed
        # by the time we get here: either set as input on the
        # itemizing / not_itemizing branch, or computed and cached on
        # the top-level sim before `refundable_ctc` was reached (the
        # `income_tax_before_credits` branch of
        # `income_tax_before_refundable_credits` runs first).
        itemizes = tax_unit("tax_unit_itemizes", period)
        no_salt_branch.set_input("tax_unit_itemizes", period, itemizes)
        tax_liability_before_credits = no_salt_branch.calculate(
            "income_tax_before_credits", period
        )
        non_refundable_credits = parameters(period).gov.irs.credits.non_refundable
        non_refundable_credits_ex_ctc = [
            x for x in non_refundable_credits if x != "non_refundable_ctc"
        ]
        total_credits = add(tax_unit, period, non_refundable_credits_ex_ctc)

        return max_(0, tax_liability_before_credits - total_credits)
