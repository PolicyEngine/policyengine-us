from policyengine_us.model_api import *


class de_income_tax_after_non_refundable_credits_indv(Variable):
    value_type = float
    entity = Person
    label = "Delaware per-person tax after non-refundable credits (PIT-RES Line 33)"
    unit = USD
    definition_period = YEAR
    reference = "https://revenuefiles.delaware.gov/2025/PITForms_Instructions/Instructions/PIT-RES_Instructions_2025-01.pdf#page=10"
    defined_for = StateCode.DE

    def formula(person, period, parameters):
        # PIT-RES Line 33: balance after non-refundable credits
        # (Lines 27a, 27b, 31), capped per column at Line 26 tax.
        # EITC (Line 34) is applied later in the main variable.
        # Note: Lines 28 (other state tax), 29 (volunteer firefighter),
        # and 30 (PIT-CRS credits) are not implemented in PolicyEngine
        # and therefore not allocated per-column here.
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)

        # Line 26: column tax from rate table.
        line26 = person("de_income_tax_before_non_refundable_credits_indv", period)

        # Lines 27a + 27b + 31, capped at Line 26 (Line 32).
        credits = (
            person("de_personal_credit_indv", period)
            + person("de_aged_personal_credit_indv", period)
            + person("de_cdcc_indv", period)
        )
        line32 = min_(credits, line26)

        return is_head_or_spouse * (line26 - line32)
