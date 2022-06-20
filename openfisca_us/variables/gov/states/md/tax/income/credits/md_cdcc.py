from openfisca_us.model_api import *


class md_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD CDCC"
    unit = USD
    definition_period = YEAR
    reference = "https://www.marylandtaxes.gov/tax-credits.php"

    def formula(tax_unit, period, parameters):
        in_md = tax_unit.household("state_code_str", period) == "MD"
        federal_cdcc = tax_unit("cdcc", period)
        match = parameters(period).gov.states.md.tax.income.credits.cdcc.match
        return in_md * federal_cdcc * match
