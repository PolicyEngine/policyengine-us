from policyengine_us.model_api import *


class tx_ottanf_crisis_criteria(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Meets Texas OTTANF crisis criteria"
    reference = (
        "https://www.law.cornell.edu/regulations/texas/1-Tex-Admin-Code-SS-372-802",
        "https://www.hhs.texas.gov/handbooks/texas-works-handbook/a-2420-eligibility-requirements",
    )
    defined_for = StateCode.TX

    # Crisis criteria per § 372.802 (b):
    # 1. Lost employment in past 2 months (not voluntary quit)
    # 2. Single parent: child lost financial support in last 12 months + parent has recent employment
    # 3. Recent graduate: unemployed/underemployed, not in school, has degree, previously received TANF
    # 4. Currently employed facing crisis: potential loss of transportation/shelter or medical emergency
    #
    # This variable has no formula - user must input whether household meets crisis criteria
