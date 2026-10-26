from policyengine_us.model_api import *


class ks_liheap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "Kansas LIEAP countable income"
    documentation = "Combined gross income of all persons living at the address counted under Kansas LIEAP, including the income of members who are not citizens or qualified aliens."
    unit = USD
    reference = (
        "https://content.dcf.ks.gov/ees/KEESM/Robo10-24/Robo_10_01_24/keesm13000.htm",
        "https://content.dcf.ks.gov/ees/KEESM/Robo01-26/Robo_01_01_26/keesm13000.htm",
        "https://content.dcf.ks.gov/ees/KEESM/Robo10-24/Robo_10_01_24/keesm13300.htm",
        "https://content.dcf.ks.gov/ees/KEESM/Robo01-26/Robo_01_01_26/keesm13300.htm",
    )
    defined_for = StateCode.KS

    adds = [
        "ks_liheap_countable_earned_income",
        "ks_liheap_countable_unearned_income",
    ]
