from policyengine_us.model_api import *


class ctc_tax_liability_after_preceding_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax liability after credits preceding the CTC"
    unit = USD
    documentation = (
        "Income tax before credits less the non-refundable credits that "
        "precede the Child Tax Credit (Schedule 8812 Credit Limit Worksheet "
        "A, line 3). Excludes SALT from income tax before credits (this is an "
        "inaccuracy required to avoid circular dependencies)."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/26#a",
        # 2025 Instructions for Schedule 8812, Credit Limit Worksheet A.
        "https://www.irs.gov/pub/irs-pdf/i1040s8.pdf#page=4",
    )

    def formula(tax_unit, period, parameters):
        simulation = tax_unit.simulation
        no_salt_branch = get_branch_for_period(simulation, "no_salt", period)
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
        p = parameters(period).gov.irs.credits.ctc_tax_liability_limit
        # add() returns None for an empty list, which a reform may set.
        preceding_credits = (
            add(tax_unit, period, p.preceding_credits) if p.preceding_credits else 0
        )
        return max_(0, tax_liability_before_credits - preceding_credits)
