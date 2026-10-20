from policyengine_us.model_api import *


class ia_ssa_rcf_daily_rate(Variable):
    value_type = float
    entity = Person
    label = "Iowa SSA approved residential care daily rate"
    definition_period = MONTH
    unit = USD
    reference = "https://hhs.iowa.gov/media/3987/download?inline=#page=72"
    documentation = "The per diem rate the department established for the facility; the model caps it at the maximum cost-related rate. Leave at 0 when no rate is approved. An entry carries into later months until it is changed."
