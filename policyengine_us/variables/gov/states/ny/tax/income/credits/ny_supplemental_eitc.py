from policyengine_us.model_api import *


class ny_supplemental_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY Supplemental EITC"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NY
    reference = "https://www.nysenate.gov/legislation/laws/TAX/606"  # (d)(8)

    def formula(tax_unit, period, parameters):
        eitc = tax_unit("earned_income_tax_credit", period)
        rate = parameters(
            period
        ).gov.states.ny.tax.income.credits.eitc.supplemental_match
        return eitc * rate
