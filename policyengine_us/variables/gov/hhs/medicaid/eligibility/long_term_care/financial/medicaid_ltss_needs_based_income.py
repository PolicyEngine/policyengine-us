from policyengine_us.model_api import *


class medicaid_ltss_needs_based_income(Variable):
    value_type = float
    entity = Person
    label = "Medicaid LTSS needs-based income"
    unit = USD
    definition_period = MONTH
    default_value = 0
    documentation = (
        "Trusted portion of QIT-adjusted income that comes from needs-based "
        "sources. The Delaware general income disregard is not applied to "
        "this portion. The model does not classify or allocate income "
        "sources."
    )
    reference = (
        "https://dhss.delaware.gov/wp-content/uploads/sites/11/2026/06/2026-SSI-Related-Income-Standards-and-Medicare-Premiums.pdf",
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/13aee487-1cd1-4726-addf-63603af28a78",
    )
