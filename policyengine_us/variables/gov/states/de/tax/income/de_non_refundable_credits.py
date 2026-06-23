from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    ordered_capped_state_non_refundable_credits,
)


class de_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Delaware non-refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DE

    def formula(tax_unit, period, parameters):
        ordered_credits = parameters(
            period
        ).gov.states.de.tax.income.credits.non_refundable
        joint_credits = ordered_capped_state_non_refundable_credits(
            tax_unit,
            period,
            ordered_credits,
            "de_income_tax_before_non_refundable_credits_unit",
        )
        # On a separate/combined return (Filing Status 4) each spouse's
        # non-refundable credits are limited to that spouse's own tax before
        # credits, so surplus credit in one column cannot offset the other
        # spouse's tax.
        person = tax_unit.members
        own_credits = person("de_non_refundable_credits_indv", period)
        indv_tax = person("de_income_tax_before_non_refundable_credits_indv", period)
        # Each spouse first applies their own (column-tied) credits against
        # their own tax.
        own_credits_used = tax_unit.sum(min_(own_credits, indv_tax))
        # Credits the filers may allocate between columns: dependents' personal
        # credits, the child/dependent care credit and the non-refundable EITC.
        # A filer minimizing tax assigns them to the column with the most
        # remaining tax (Form PIT-RES lets exemptions be allocated between
        # columns). Place the whole allocable amount in the higher-capacity
        # column, capped at that column's remaining tax.
        p = parameters(period).gov.states.de.tax.income.credits.personal_credits
        dependents = tax_unit("tax_unit_dependents", period)
        allocable_credits = (
            dependents * p.personal
            + tax_unit("de_cdcc_potential", period)
            + tax_unit("de_non_refundable_eitc_potential", period)
        )
        remaining_capacity = max_(indv_tax - own_credits, 0)
        largest_remaining_capacity = tax_unit.max(remaining_capacity)
        allocable_used = min_(allocable_credits, largest_remaining_capacity)
        separate_credits = own_credits_used + allocable_used
        files_separately = tax_unit("de_files_separately", period)
        return where(files_separately, separate_credits, joint_credits)
