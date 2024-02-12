from policyengine_us.model_api import *


class ky_income_tax_before_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kentucky income tax before refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.KY

    def formula(tax_unit, period, paramters):
        tax_before_non_refundable = tax_unit(
            "ky_income_tax_before_non_refundable_credits", period
        )
        ky_files_separately = tax_unit("ky_files_separately", period)
        person = tax_unit.members
        ky_personal_tax_credits_indiv = person(
            "ky_personal_tax_credits_indiv", period
        )
        ky_personal_tax_credits_joint = person(
            "ky_personal_tax_credits_joint", period
        )
        ky_personal_tax_credits = where(
            ky_files_separately,
            tax_unit.sum(ky_personal_tax_credits_indiv),
            tax_unit.sum(ky_personal_tax_credits_joint),
        )
        other_non_refundable_credits = tax_unit(
            "ky_non_refundable_credits", period
        )
        non_refundable_credits = (
            other_non_refundable_credits + ky_personal_tax_credits
        )

        return max_(tax_before_non_refundable - non_refundable_credits, 0)
