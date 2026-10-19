from policyengine_us.model_api import *


class ky_family_size_tax_credit_rate(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kentucky family size tax credit rate"
    unit = "/1"
    documentation = (
        "The rate on the filing path the tax unit elects. "
        "ky_family_size_tax_credit_rate_if_joint and "
        "ky_family_size_tax_credit_rate_if_separate give each path's rate."
    )
    definition_period = YEAR
    reference = "https://apps.legislature.ky.gov/law/statutes/statute.aspx?id=49188"
    defined_for = StateCode.KY

    def formula(tax_unit, period, parameters):
        income = tax_unit("ky_modified_agi", period)
        threshold = tax_unit("ky_family_size_tax_credit_threshold", period)
        p = parameters(period).gov.states.ky.tax.income.credits.family_size
        return p.rate.calc(income / threshold, right=True)
