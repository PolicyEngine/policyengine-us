from policyengine_us.model_api import *


class al_federal_tax_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Alabama federal tax deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://www.revenue.alabama.gov/ultraviewer/viewer/basic_viewer/index.html?form=2023/01/22f40abk.pdf#page=20"
    defined_for = StateCode.AL
