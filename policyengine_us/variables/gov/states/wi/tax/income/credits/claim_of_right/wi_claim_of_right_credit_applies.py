from policyengine_us.model_api import *


class wi_claim_of_right_credit_applies(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Filer takes the Wisconsin claim of right credit over the subtraction"
    documentation = (
        "Whether the filer takes the Wisconsin claim of right credit (Wis. "
        "Stat. 71.07(1)) instead of subtracting the repayment from income "
        "(71.05(6)(b)29). The same repayment cannot be used for both. The "
        "choice does not depend on the federal method. It is derived, not "
        "elected: the model computes Wisconsin income tax both ways and "
        "takes the lower, and the subtraction when the two are equal."
    )
    definition_period = YEAR
    reference = (
        "https://docs.legis.wisconsin.gov/statutes/statutes/71/i/07/1",
        "https://docs.legis.wisconsin.gov/statutes/statutes/71/i/05/6/b/29",
        # 2025 Schedule SB instructions, line 28: "you may be able to
        # subtract the repayment as described above or take a tax credit"
        "https://www.revenue.wi.gov/TaxForms2025/2025-ScheduleSB-Inst.pdf#page=11",
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        eligible = tax_unit("wi_claim_of_right_eligible", period)
        if not eligible.any():
            # Comparing the two takes two more tax computations; skip them
            # when no Wisconsin tax unit repays more than the threshold.
            return np.zeros(tax_unit.count, dtype=bool)
        tax_if_credit = tax_unit(
            "wi_income_tax_if_claiming_claim_of_right_credit", period
        )
        tax_if_subtraction = tax_unit(
            "wi_income_tax_if_claiming_claim_of_right_subtraction", period
        )
        # Ties go to the subtraction; the tolerance keeps floating-point
        # noise from deciding a tie.
        TOLERANCE = 0.01
        return eligible & (tax_if_credit < tax_if_subtraction - TOLERANCE)
