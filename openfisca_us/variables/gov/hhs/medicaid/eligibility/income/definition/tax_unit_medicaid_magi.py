from openfisca_us.model_api import *


class tax_unit_medicaid_magi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax unit medicaid-related MAGI"
    unit = USD
    documentation = "Income definition for Medicaid for this tax unit."
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/36B#d_2"

    def formula(tax_unit, period, parameters):
        agi = tax_unit("adjusted_gross_income", period)
        income_additions = parameters(
            period
        ).hhs.medicaid.income.additions_over_agi
        return max_(0, agi + add(tax_unit, period, income_additions))
