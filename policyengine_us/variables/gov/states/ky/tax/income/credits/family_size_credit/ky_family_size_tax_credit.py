from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    applied_state_non_refundable_credit,
)


class ky_family_size_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kentucky family size tax credit"
    unit = "/1"
    definition_period = YEAR
    reference = "https://apps.legislature.ky.gov/law/statutes/statute.aspx?id=49188"
    defined_for = StateCode.KY

    def formula(tax_unit, period, parameters):
        ordered_credits = parameters(
            period
        ).gov.states.ky.tax.income.credits.non_refundable
        return applied_state_non_refundable_credit(
            tax_unit,
            period,
            ordered_credits,
            "ky_income_tax_before_non_refundable_credits_unit",
            "ky_family_size_tax_credit",
            "ky_family_size_tax_credit_potential",
        )
