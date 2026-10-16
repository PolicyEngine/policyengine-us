from policyengine_us.model_api import *


class ia_ssa_rcf_daily_rate(Variable):
    value_type = float
    entity = Person
    label = "Iowa SSA approved residential care daily rate"
    definition_period = MONTH
    unit = USD
    reference = ("https://hhs.iowa.gov/media/3987/download?inline=",)
