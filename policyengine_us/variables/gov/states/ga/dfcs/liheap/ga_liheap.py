from policyengine_us.model_api import *


class ga_liheap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Georgia LIHEAP ordinary heating benefit"
    defined_for = "ga_liheap_eligible"
    reference = (
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/GA_BenefitMatrix_Heat-Cool_2026.pdf",
        "https://liheapch.acf.gov/sites/default/files/webfiles/docs/2023/manuals/GA_PolicyManual_2023.pdf#page=4",
    )
    # The ordinary grant is a fixed schedule amount with no bill cap. Unpriced
    # fuels and the matrix's size-above-16 approximation remain unverified.
    adds = ["ga_liheap_matrix_amount"]
