from policyengine_us.model_api import *


class ky_family_size_tax_credit_rate_if_separate(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kentucky family size tax credit rate on the combined-separate path"
    unit = "/1"
    definition_period = YEAR
    reference = "https://apps.legislature.ky.gov/law/statutes/statute.aspx?id=49188"
    defined_for = StateCode.KY

    def formula(tax_unit, period, parameters):
        income = tax_unit("ky_modified_agi_if_separate", period)
        threshold = tax_unit("ky_family_size_tax_credit_threshold", period)
        p = parameters(period).gov.states.ky.tax.income.credits.family_size
        return p.rate.calc(income / threshold, right=True)
