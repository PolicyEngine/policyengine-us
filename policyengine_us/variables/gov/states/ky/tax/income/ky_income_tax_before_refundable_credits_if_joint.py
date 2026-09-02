from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.ky.tax.income._ky_combined_separate import (
    ky_income_tax_after_non_refundable_credits_for_path,
)


class ky_income_tax_before_refundable_credits_if_joint(Variable):
    value_type = float
    entity = TaxUnit
    # The `_if_` prefix is deliberate: it disambiguates these TaxUnit
    # path-scenario variables (comparing the joint and combined-separate
    # elections) from the pre-existing Person-level
    # ky_income_tax_before_non_refundable_credits_joint.
    label = "Kentucky income tax before refundable credits on the joint path"
    unit = USD
    definition_period = YEAR
    reference = (
        # Combined-separate column structure (file p. 11).
        "https://revenue.ky.gov/Forms/740%20Packet%20Instructions%205-9-23.pdf#page=11",
        # Line 19 combined-return credit application (file p. 12).
        "https://revenue.ky.gov/Forms/740%20Packet%20Instructions%205-9-23.pdf#page=12",
        # KRS 141.0205(2)(a)-(d) "Priority of application and use of tax
        # credits" prescribes the personal -> family size -> tuition ->
        # dependent care order the helper applies.
        "https://apps.legislature.ky.gov/law/statutes/statute.aspx?id=57934",
        # 2025 Form 740 (tests run at 2025): same combined-return structure.
        "https://revenue.ky.gov/Forms/740%20(2025).pdf",
    )
    defined_for = StateCode.KY

    def formula(tax_unit, period, parameters):
        base = add(
            tax_unit,
            period,
            ["ky_income_tax_before_non_refundable_credits_joint"],
        )
        # Joint: personal credits are pooled at the tax-unit level.
        personal_potential = add(tax_unit, period, ["ky_personal_tax_credits_joint"])
        return ky_income_tax_after_non_refundable_credits_for_path(
            tax_unit, period, base, personal_potential
        )
