from policyengine_us.model_api import *


class is_demographic_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Demographic eligibility for TANF"
    documentation = "Whether any person in a family applying for the Temporary Assistance for Needy Families program meets demographic requirements."
    adds = ["is_person_demographic_tanf_eligible"]
