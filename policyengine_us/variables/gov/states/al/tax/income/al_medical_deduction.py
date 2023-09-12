from policyengine_us.model_api import *


class al_medical_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Alabama Medical Deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.alabama.gov/ultraviewer/viewer/basic_viewer/index.html?form=2023/01/22f40schabdc_blk.pdf"
        "https://www.revenue.alabama.gov/ultraviewer/viewer/basic_viewer/index.html?form=2023/02/22f40.pdf"
    )
    defined_for = StateCode.AL

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.al.tax.income.deductions.itemized
        medical_deduction = tax_unit("al_medical_dedcution", period)
        deduction_value = p.medical_expense * medical_deduction
        return deduction_value
