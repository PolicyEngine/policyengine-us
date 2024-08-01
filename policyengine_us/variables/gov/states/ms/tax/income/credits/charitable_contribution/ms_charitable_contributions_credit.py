from policyengine_us.model_api import *


class ms_charitable_contributions_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Mississippi charitable contributions credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MS
    reference = (
        "https://www.dor.ms.gov/sites/default/files/Forms/Individual/80100211_0.pdf#page=18",
        "https://www.dor.ms.gov/sites/default/files/Forms/Individual/80100231.pdf#page=3",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.ms.tax.income.credits.charitable_contribution

        foster_care_contributions = tax_unit(
            "ms_charitable_contributions_to_qualifying_foster_care_organizations",
            period,
        )
        filing_status = tax_unit("filing_status", period)
        cap = p.cap[filing_status]

        return min_(foster_care_contributions, cap)
