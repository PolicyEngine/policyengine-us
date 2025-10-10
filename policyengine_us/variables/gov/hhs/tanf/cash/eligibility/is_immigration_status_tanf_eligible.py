from policyengine_us.model_api import *


class is_immigration_status_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Immigration Status eligibility for TANF"
    documentation = "Whether any person in a family applying for the Temporary Assistance for Needy Families program meets immigration status requirements."
    adds = ["is_person_immigration_status_tanf_eligible"]
