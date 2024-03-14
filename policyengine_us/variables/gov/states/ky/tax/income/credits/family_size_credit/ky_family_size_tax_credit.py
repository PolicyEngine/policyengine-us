from policyengine_us.model_api import *


class ky_family_size_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kentucky family size tax credit"
    unit = "/1"
    definition_period = YEAR
    reference = (
        "https://apps.legislature.ky.gov/law/statutes/statute.aspx?id=49188"
    )
    defined_for = StateCode.KY

    def formula(tax_unit, period, parameters):
        rate = tax_unit("ky_family_size_tax_credit_rate", period)
        income = tax_unit(
            "ky_income_tax_before_non_refundable_credits_unit", period
        )
        personal_credits = tax_unit("ky_personal_tax_credits", period)
        reduced_income = max_(income - personal_credits, 0)

        return rate * reduced_income
