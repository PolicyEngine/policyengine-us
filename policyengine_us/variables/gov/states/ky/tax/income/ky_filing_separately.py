from policyengine_us.model_api import *


class ky_files_separately(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Married couple files separately on the Kentucky tax return"
    definition_period = YEAR
    reference = (
        # Filing Status 2 (combined-separate) description (file p. 11).
        "https://revenue.ky.gov/Forms/740%20Packet%20Instructions%205-9-23.pdf#page=11",
        # Line 19 combined-return credit application (file p. 12).
        "https://revenue.ky.gov/Forms/740%20Packet%20Instructions%205-9-23.pdf#page=12",
        # KRS 141.0205(2) prescribes the post-election application of the
        # nonrefundable personal tax credits used to compare the paths.
        "https://apps.legislature.ky.gov/law/statutes/statute.aspx?id=57934",
    )
    defined_for = StateCode.KY

    def formula(tax_unit, period, parameters):
        # Combined-separate (Form 740 Filing Status 2) is only available to
        # married couples; single and head-of-household filers use the joint
        # (single-column) path. A couple is represented either by a spouse in
        # the tax unit or by a joint filing status, so accept either. The model
        # gates the election on MARRIED only, a deliberate simplification of
        # Form 740's "both spouses had income" condition: under the post-credit
        # election a zero-income spouse's column offers no advantage and only
        # strands credits, so the joint path weakly dominates and the gate is
        # harmless.
        filing_status = tax_unit("filing_status", period)
        is_joint = filing_status == filing_status.possible_values.JOINT
        has_spouse = add(tax_unit, period, ["is_tax_unit_spouse"]) > 0
        is_married_couple = is_joint | has_spouse

        # Kentucky filers elect the path that minimises tax. The election is
        # made on liability AFTER non-refundable credits: combined-separate
        # filing can waste personal credits when a spouse's column tax is too
        # low to absorb them (e.g. an over-65 spouse with only retirement income
        # whose $40 credit is lost), so the optimal choice can flip once credits
        # are applied. Comparing tax before credits (the previous behaviour)
        # wrongly elected combined-separate for a tiny pre-credit saving and then
        # forfeited the credit. Refundable credits are path-independent and do
        # not affect the election.
        separate = tax_unit(
            "ky_income_tax_before_refundable_credits_if_separate", period
        )
        joint = tax_unit("ky_income_tax_before_refundable_credits_if_joint", period)
        return is_married_couple & (separate < joint)
