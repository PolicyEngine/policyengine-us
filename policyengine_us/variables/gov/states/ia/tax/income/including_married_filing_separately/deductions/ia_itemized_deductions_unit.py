from policyengine_us.model_api import *


class ia_itemized_deductions_unit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Iowa itemized deductions for tax unit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenue.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdf",
        "https://revenue.iowa.gov/media/2650/download?inline",
        "https://revenue.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdf",
        "https://revenue.iowa.gov/media/2721/download?inline",
        # 2018 IA Schedule A, line 26.
        "https://revenue.iowa.gov/media/2298/download?inline=#page=1",
    )
    defined_for = StateCode.IA
    adds = ["ia_itemized_deductions_pre_limitation"]
    subtracts = ["ia_itemized_deductions_reduction"]
