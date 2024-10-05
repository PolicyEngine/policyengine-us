from policyengine_us.model_api import *


class al_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Alabama taxable income"
    defined_for = StateCode.AL
    unit = USD
    definition_period = YEAR
    reference = "https://www.revenue.alabama.gov/ultraviewer/viewer/basic_viewer/index.html?form=2023/01/22f40abk.pdf"  # 2022 Form 40A Booklet

    def formula(tax_unit, period, parameters):
        al_ded = tax_unit("al_deductions", period)
        al_agi = tax_unit("al_agi", period)
        return max_(al_agi - al_ded, 0)
