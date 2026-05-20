from policyengine_us.model_api import *


class ca_scc_general_assistance_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    definition_period = MONTH
    label = "Santa Clara County General Assistance countable income"
    defined_for = "in_scc"
    reference = "https://stgenssa.sccgov.org/debs/program_handbooks/general_assistance/assets/09Income/GA_Policies.htm"

    adds = ["ca_scc_general_assistance_countable_income_person"]
