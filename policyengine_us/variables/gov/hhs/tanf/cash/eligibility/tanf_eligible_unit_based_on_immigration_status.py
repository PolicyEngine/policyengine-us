from policyengine_us.model_api import *


class is_tanf_eligible_based_on_immigration_status(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Immigration Status eligibility for TANF"
    documentation = "Whether any person in a family applying for the Temporary Assistance for Needy Families program meets immigration status requirements."
    adds = ["is_tanf_eligible_person_based_on_immigration_status"]
