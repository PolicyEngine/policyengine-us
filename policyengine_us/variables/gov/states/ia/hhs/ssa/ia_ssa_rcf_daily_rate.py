from policyengine_us.model_api import *


class ia_ssa_rcf_daily_rate(Variable):
    value_type = float
    entity = Person
    label = "Iowa SSA approved residential care daily rate"
    definition_period = MONTH
    unit = USD
    default_value = 0
    reference = (
        # 441 IAC 52.1(3)
        "https://www.legis.iowa.gov/docs/iac/chapter/441.52.pdf#page=1",
        "https://hhs.iowa.gov/media/3987/download?inline=#page=72",
    )
    documentation = "A per diem rate below the maximum that the department established for the facility. Leave at 0 to pay the maximum per diem rate, as 441 IAC 52.1(3) provides from July 1, 2017; an entry above the maximum is capped. An entry carries into later months until it is changed."
