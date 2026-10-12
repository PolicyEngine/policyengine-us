from policyengine_us.model_api import *


class ia_ssa_ihhrc_initial_partial_month(Variable):
    value_type = bool
    entity = Person
    label = "Iowa IHHRC initial partial month without client participation"
    definition_period = MONTH
    reference = ("https://hhs.iowa.gov/media/3987/download?inline=",)
