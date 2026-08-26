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
    capped at the liability remaining after earlier credits.

    This helper does not read ``ky_files_separately``, so the combined-separate
    election can compare the two paths without a circular dependency.
    """
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
