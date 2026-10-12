"""Drift guard for the Kentucky non-refundable credit order.

The combined-separate election helper
(policyengine_us/variables/gov/states/ky/tax/income/_ky_combined_separate.py)
hard-codes the credit application order personal -> family size -> tuition ->
dependent care to compare the joint and combined-separate paths without a
circular dependency. The post-election chain derives the same order from the
gov.states.ky.tax.income.credits.non_refundable parameter list. If that list is
reordered or extended, the helper must be updated to match; this test fails so
the divergence is caught in CI.
"""

from policyengine_us import CountryTaxBenefitSystem

EXPECTED_2022_ORDER = [
    "ky_personal_tax_credits",
    "ky_family_size_tax_credit",
    "ky_tuition_tax_credit",
    "ky_cdcc",
]


def test_ky_non_refundable_credit_order_2022():
    parameters = CountryTaxBenefitSystem().parameters
    credit_list = parameters.gov.states.ky.tax.income.credits.non_refundable(
        "2022-01-01"
    )
    assert list(credit_list) == EXPECTED_2022_ORDER
