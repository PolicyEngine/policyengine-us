from policyengine_us.model_api import *


class alimony_expense_ald(Variable):
    value_type = float
    entity = TaxUnit
    label = "Alimony expense ALD"
    unit = USD
    documentation = "Above-the-line deduction from gross income for alimony expenses."
    definition_period = YEAR
    reference = "https://www.irs.gov/taxtopics/tc452"

    def formula(tax_unit, period, parameters):
        # A tax unit dependent who pays alimony deducts it on their own return.
        return tax_unit_non_dep_sum("alimony_expense_ald_person", tax_unit, period)
