from policyengine_us.model_api import *


class ks_liheap_household_size(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Kansas LIEAP household size"
    documentation = "Number of household members who are U.S. citizens or qualified aliens. Other members are not counted in household size, although their income counts toward household income."
    reference = "https://content.dcf.ks.gov/ees/keesm/current/keesm13300.htm"
    defined_for = StateCode.KS

    adds = ["is_citizen_or_legal_immigrant"]
