from policyengine_us.model_api import *


class ia_ssa_smme_coverage_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Iowa SMME full Medicaid and Medicare Part B requirements met"
    definition_period = MONTH
    reference = ("https://hhs.iowa.gov/media/3987/download?inline=",)
    documentation = "Receiving full Medicaid under a category independent of SSA without a premium or spenddown, and eligible for Medicare Part B. Ordinary Medicaid enrollment alone does not establish this status."
