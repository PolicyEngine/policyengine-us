from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.ky.tax.income._ky_combined_separate import (
    ky_income_tax_after_non_refundable_credits_for_path,
)


class ky_income_tax_before_refundable_credits_if_separate(Variable):
    value_type = float
    entity = TaxUnit
    label = (
        "Kentucky income tax before refundable credits on the combined-separate path"
    )
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
        person = tax_unit.members
        indiv_base = person("ky_income_tax_before_non_refundable_credits_indiv", period)
        base = tax_unit.sum(indiv_base)
        # Combined-separate: each spouse's personal credit offsets only their
        # own column's tax (Form 740 lines 16-18), so cap per column before
        # summing.
        indiv_personal = person("ky_personal_tax_credits_indiv", period)
        personal_potential = tax_unit.sum(min_(indiv_personal, indiv_base))
        return ky_income_tax_after_non_refundable_credits_for_path(
            tax_unit, period, base, personal_potential
        )
