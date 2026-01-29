from policyengine_us.model_api import *
import numpy as np


class or_healthier_oregon_immigration_status_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Has eligible immigration status for Oregon Healthier Oregon"
    definition_period = YEAR
    defined_for = StateCode.OR
    reference = (
        "https://www.oregon.gov/oha/hsd/ohp/pages/healthier-oregon.aspx",
        "https://olis.oregonlegislature.gov/liz/2021R1/Downloads/MeasureDocument/HB3352/Enrolled",
    )

    def formula(person, period, parameters):
        p = (
            parameters(period)
            .gov.states["or"]
            .oha.healthier_oregon.eligibility
        )
        immigration_status = person("immigration_status", period)
        immigration_status_str = immigration_status.decode_to_str()
        return np.isin(
            immigration_status_str,
            p.qualified_immigration_statuses,
        )
