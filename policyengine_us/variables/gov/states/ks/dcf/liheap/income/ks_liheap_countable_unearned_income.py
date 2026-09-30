from policyengine_us.model_api import *


class ks_liheap_countable_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "Kansas LIEAP countable unearned income"
    documentation = "Gross unearned income of all household members counted toward Kansas LIEAP household income."
    unit = USD
    reference = (
        "https://content.dcf.ks.gov/ees/KEESM/Robo10-24/Robo_10_01_24/keesm13360.htm",
        "https://content.dcf.ks.gov/ees/KEESM/Robo01-26/Robo_01_01_26/keesm13360.htm",
        "https://liheapch.acf.gov/docs/2026/state-plans/KS_Plan_2026.pdf#page=6",
    )
    defined_for = StateCode.KS

    adds = "gov.states.ks.dcf.liheap.income.sources.unearned"
