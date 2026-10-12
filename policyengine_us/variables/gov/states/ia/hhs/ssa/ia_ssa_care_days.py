from policyengine_us.model_api import *


class ia_ssa_care_days(Variable):
    value_type = int
    entity = Person
    label = "Iowa SSA covered care days"
    definition_period = MONTH
    reference = ("https://hhs.iowa.gov/media/3987/download?inline=",)
    documentation = "Covered residential days include admission but not discharge/death, plus authorized reserve bed days. For IHHRC, days of approved services in a partial month."

    def formula(person, period, parameters):
        return period.days
