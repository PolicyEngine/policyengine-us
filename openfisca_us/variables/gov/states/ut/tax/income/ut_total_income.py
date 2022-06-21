from openfisca_us.model_api import *


class ut_total_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "UT total income"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        federal_agi = tax_unit("adjusted_gross_income", period)
        ut_additions = tax_unit("ut_additions_to_income", period)

        return federal_agi + ut_additions
