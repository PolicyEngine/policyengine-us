from policyengine_us.model_api import *


class state_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "state income tax"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        if parameters(period).simulation.reported_state_income_tax:
            spm_unit = tax_unit.spm_unit
            person = spm_unit.members
            is_head = person("is_tax_unit_head", period)
            total_tax_unit_heads = spm_unit.sum(is_head)
            spm_unit_state_tax = spm_unit(
                "spm_unit_state_tax_reported", period
            )
            return where(
                total_tax_unit_heads > 0,
                spm_unit_state_tax / total_tax_unit_heads,
                0,
            )
        else:
            income_tax_before_refundable_credits = add(
                tax_unit,
                period,
                ["state_income_tax_before_refundable_credits"],
            )
            refundable_credits = add(
                tax_unit, period, ["state_refundable_credits"]
            )
            return income_tax_before_refundable_credits - refundable_credits
