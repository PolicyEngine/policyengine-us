from policyengine_us.model_api import *


class al_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Alabama itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.alabama.gov/ultraviewer/viewer/basic_viewer/index.html?form=2023/01/22f40schabdc_blk.pdf"
        "https://www.revenue.alabama.gov/ultraviewer/viewer/basic_viewer/index.html?form=2023/02/22f40.pdf"
    )
    defined_for = StateCode.AL

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.al.tax.income.deductions
        deduction_value = add(tax_unit, period, p.itemized)
        return deduction_value
