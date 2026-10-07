from policyengine_us.model_api import *


class ky_disallowed_second_residence_interest(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kentucky disallowed second-residence interest deduction"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Federal qualified residence interest on a second residence, "
        "including points and mortgage insurance premiums, that Kentucky "
        "removes from itemized deductions once it limits the deduction to "
        "the principal residence."
    )
    reference = (
        "https://apps.legislature.ky.gov/law/statutes/statute.aspx?id=57914#page=4",  # (2)(j)
        "https://apps.legislature.ky.gov/law/acts/26RS/documents/0161.pdf#page=13",
        "https://apps.legislature.ky.gov/law/acts/26RS/documents/0198.pdf#page=74",
    )
    defined_for = StateCode.KY

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ky.tax.income.deductions.itemized
        second_residence = tax_unit("second_residence_interest_deduction", period)
        return second_residence * p.principal_residence_interest_only
