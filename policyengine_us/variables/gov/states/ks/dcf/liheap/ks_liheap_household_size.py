from policyengine_us.model_api import *


class ks_liheap_household_size(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Kansas LIEAP household size"
    documentation = "Number of household members who are U.S. citizens or qualified aliens. Other members are not counted in household size, although their income counts toward household income."
    reference = (
        "https://content.dcf.ks.gov/ees/KEESM/Robo10-24/Robo_10_01_24/keesm13300.htm",
        "https://content.dcf.ks.gov/ees/KEESM/Robo01-26/Robo_01_01_26/keesm13300.htm",
    )
    defined_for = StateCode.KS

    adds = ["is_citizen_or_legal_immigrant"]
