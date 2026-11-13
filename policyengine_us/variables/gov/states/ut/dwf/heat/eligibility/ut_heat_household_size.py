from policyengine_us.model_api import *


class ut_heat_household_size(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Utah HEAT eligible household size"
    defined_for = StateCode.UT
    reference = "https://jobs.utah.gov/infosource/heatpolicy/Policy/200_Program_Standards/204_Eligibility_with_Ineligible_Resident.htm"
    # SPM units approximate the shared residence and energy-cost unit. Temporary
    # guests, absences, shared custody and the foster-child election are unobserved.
    adds = ["ut_heat_eligible_person"]
