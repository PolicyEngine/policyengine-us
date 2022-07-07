from openfisca_us.model_api import *


class il_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "IL adjusted gross income"
    unit = USD
    definition_period = YEAR
    reference = ""

    def formula(tax_unit, period, parameters):
        federal_agi = tax_unit("adjusted_gross_income", period)
        il_additions = tax_unit("il_additions", period)
        il_subtractions = tax_unit("il_subtractions", period)
        il_exemptions = tax_unit("il_exemptions", period)

        return federal_agi + il_additions - il_subtractions - il_exemptions
