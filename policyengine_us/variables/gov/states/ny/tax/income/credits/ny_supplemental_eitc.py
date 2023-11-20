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
        federal_eitc = tax_unit("eitc", period)
        p = parameters(period).gov.states.ny.tax.income.credits
        return federal_eitc * p.eitc.supplemental_match
