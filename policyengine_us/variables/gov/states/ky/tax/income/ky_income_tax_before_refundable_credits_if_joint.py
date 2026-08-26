from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.ky.tax.income.ky_combined_separate import (
    ky_income_tax_after_non_refundable_credits_for_path,
)


class ky_income_tax_before_refundable_credits_if_joint(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kentucky income tax before refundable credits on the joint path"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenue.ky.gov/Forms/740%20Packet%20Instructions%205-9-23.pdf#page=11"
    )
    defined_for = StateCode.KY

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        base = tax_unit.sum(
            person("ky_income_tax_before_non_refundable_credits_joint", period)
        )
        # Joint: personal credits are pooled at the tax-unit level.
        personal_potential = tax_unit.sum(
            person("ky_personal_tax_credits_joint", period)
        )
        return ky_income_tax_after_non_refundable_credits_for_path(
            tax_unit, period, base, personal_potential
        )
