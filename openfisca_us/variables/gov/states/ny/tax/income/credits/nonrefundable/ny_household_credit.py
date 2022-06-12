from openfisca_us.model_api import *


class ny_household_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY household credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/606"  # (b)

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).states.ny.tax.income.credits.nonrefundable.household_credit
        filing_status = tax_unit("filing_status", period)
        filing_statuses = filing_status.possible_values
        agi = tax_unit("adjusted_gross_income", period)
        # Single filers: based only on AGI.
        single = filing_status == filing_statuses.SINGLE
        # Use `right=True` to reflect "over...but not over".
        amount_if_single = p.single.calc(agi, right=True)
        single_amount = single * amount_if_single
        # Joint, head of household, and widow(er) filers: based on AGI & size.
        size = tax_unit("tax_unit_size", period)
        joint_head_widow = (
            (filing_status == filing_statuses.JOINT)
            | (filing_status == filing_statuses.HEAD_OF_HOUSEHOLD)
            | (filing_status == filing_statuses.WIDOW)
        )
        joint_head_widow_base = p.joint_head_widow.base.calc(agi, right=True)
        joint_head_widow_additional = p.joint_head_widow.additional.calc(
            agi, right=True
        )
        amount_if_joint_head_widow = (
            joint_head_widow_base + joint_head_widow_additional * (size - 1)
        )
        joint_head_widow_amount = joint_head_widow * amount_if_joint_head_widow
        return single_amount + joint_head_widow_amount
