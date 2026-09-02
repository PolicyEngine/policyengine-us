from policyengine_us.model_api import *


def ky_income_tax_after_non_refundable_credits_for_path(
    tax_unit, period, base, personal_potential
):
    """Kentucky income tax after the four ordered non-refundable credits, on a
    fixed filing path.

    ``base`` is the Kentucky income tax before non-refundable credits on that
    path and ``personal_potential`` the personal tax credit available on it
    (each spouse's credit capped at their own column tax on the combined-separate
    path; pooled across the tax unit on the joint path). Form 740 applies the
    credits in order -- personal, family size, tuition, dependent care -- each
    capped at the liability remaining after earlier credits. KRS 141.0205(2)(a)-(d)
    "Priority of application and use of tax credits" prescribes exactly this order
    (personal, family size 141.066, tuition 141.069, dependent care 141.067):
    https://apps.legislature.ky.gov/law/statutes/statute.aspx?id=57934

    KRS 141.0205 subsection (1) business-incentive credits precede, and (2)(e) the
    income-gap credit (2021 only) and (2)(f) the Education Opportunity Account
    credit follow, these four (2)(a)-(d) credits; none of those are modeled, so
    (a)-(d) is the complete ordered set for the modeled credits.

    This helper does not read ``ky_files_separately``, so the combined-separate
    election can compare the two paths without a circular dependency.
    """
    # NOTE: this helper hard-codes the personal -> family size -> tuition ->
    # dependent care (CDCC) order. The post-election chain
    # (ky_non_refundable_credits -> ordered_capped_state_non_refundable_credits)
    # derives the SAME order from
    # parameters/gov/states/ky/tax/income/credits/non_refundable.yaml. If a
    # credit is added to or reordered within that parameter list, mirror the
    # change here so the election and the final liability stay consistent.
    # 1. Personal tax credits (Form 740 lines 16-18).
    applied_personal = min_(personal_potential, max_(base, 0))
    remaining = max_(base - applied_personal, 0)
    # 2. Family size tax credit: rate x (tax before credits less personal
    #    credits), matching ky_family_size_tax_credit_potential.
    rate = tax_unit("ky_family_size_tax_credit_rate", period)
    applied_family = min_(rate * remaining, remaining)
    remaining = max_(remaining - applied_family, 0)
    # 3. Tuition tax credit (path-neutral potential).
    tuition_potential = tax_unit("ky_tuition_tax_credit_potential", period)
    remaining = max_(remaining - min_(tuition_potential, remaining), 0)
    # 4. Household and dependent care credit (path-neutral potential).
    cdcc_potential = tax_unit("ky_cdcc_potential", period)
    remaining = max_(remaining - min_(cdcc_potential, remaining), 0)
    return remaining
