from policyengine_us.model_api import *


class ia_ssa_countable_for_snap(Variable):
    value_type = float
    entity = Person
    label = "Iowa State Supplementary Assistance countable for SNAP"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.IA
    reference = (
        "https://hhs.iowa.gov/media/3997#page=34",
        "https://www.ecfr.gov/current/title-7/section-273.9#p-273.9(c)(5)",
    )

    def formula(person, period, parameters):
        # Iowa SNAP manual 7-E: "Exclude State Supplementary Assistance payments
        # made for in-home health-related care as a reimbursement" (7 CFR
        # 273.9(c)(5)). The blind supplement paid alongside it remains
        # countable cash assistance.
        category = person("ia_ssa_category", period)
        home_care = category == category.possible_values.IN_HOME_CARE
        return where(
            home_care, person("ia_ssa_federal", period), person("ia_ssa", period)
        )
