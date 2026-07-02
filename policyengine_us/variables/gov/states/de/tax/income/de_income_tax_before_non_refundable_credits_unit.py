from policyengine_us.model_api import *


class de_income_tax_before_non_refundable_credits_unit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Delaware personal income tax before non-refundable credits combined"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DE

    def formula(tax_unit, period, parameters):
        # The combined separate (FS4) path applies non-refundable credits
        # per column (see de_income_tax_before_refundable_credits_separate),
        # so this pooled pre-credit total only serves the joint/combined path
        # and always reflects the joint computation. Keeping it independent of
        # de_files_separately lets that election be made on post-credit
        # liability without a circular dependency (issue #7931).
        return add(
            tax_unit,
            period,
            ["de_income_tax_before_non_refundable_credits_joint"],
        )
