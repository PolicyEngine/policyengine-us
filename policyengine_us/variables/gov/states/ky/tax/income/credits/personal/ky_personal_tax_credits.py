from policyengine_us.model_api import *


class ky_personal_tax_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kentucky personal tax credits"
    unit = USD
    documentation = (
        "https://apps.legislature.ky.gov/law/statutes/statute.aspx?id=53500"
    )
    definition_period = YEAR
    defined_for = StateCode.KY

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ky.tax.income.credits.personal
        adds = [
            "ky_personal_tax_credits_blind",
            "ky_personal_tax_credits_aged",
            "ky_personal_tax_credits_military",
        ]
        return add(tax_unit, period, adds)
