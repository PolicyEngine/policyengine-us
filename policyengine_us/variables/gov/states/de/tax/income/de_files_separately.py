from policyengine_us.model_api import *


class de_files_separately(Variable):
    value_type = bool
    entity = TaxUnit
    label = "married couple files separately on the Delaware tax return"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenuefiles.delaware.gov/2022/PIT-RES_TY22_2022-02_Instructions.pdf"
    )
    defined_for = StateCode.DE

    def formula(tax_unit, period, parameters):
        # Combined separate (Filing Status 4) is only available to married
        # couples; single and head-of-household filers always use the joint
        # (single-column) path.
        has_spouse = add(tax_unit, period, ["is_tax_unit_spouse"]) > 0

        # Delaware filers elect the filing status that minimises their tax.
        # The election is made on liability AFTER non-refundable credits,
        # because combined separate filing (FS4) can waste credits when a
        # column's tax is too low to absorb its share, so the optimal choice
        # can flip once credits are applied (issue #7931). Refundable credits
        # are path-independent and so do not affect the election.
        separate = tax_unit("de_income_tax_before_refundable_credits_separate", period)
        joint = tax_unit("de_income_tax_before_refundable_credits_joint", period)
        return has_spouse & (separate < joint)
