from policyengine_us.model_api import *


class al_federal_income_tax_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Alabama federal income tax deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://www.revenue.alabama.gov/ultraviewer/viewer/basic_viewer/index.html?form=2023/01/22f40abk.pdf#page=20"
    defined_for = StateCode.AL

    adds = "gov.states.al.tax.income.deductions.federal_tax.countable_sources"

    subtracts = "gov.states.al.tax.income.deductions.federal_tax.credits"
