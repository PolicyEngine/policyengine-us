from policyengine_us.model_api import *


class ks_liheap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Kansas LIEAP income eligible"
    documentation = "Countable household income does not exceed the published seasonal income limit. Kansas reuses income verified for other benefits but still tests total household income. Annual income represents twelve times income in the application month."
    reference = (
        "https://content.dcf.ks.gov/ees/KEESM/Robo10-24/Robo_10_01_24/keesm13360.htm",
        "https://content.dcf.ks.gov/ees/KEESM/Robo01-26/Robo_01_01_26/keesm13360.htm",
        "https://liheapch.acf.gov/docs/2026/state-plans/KS_Plan_2026.pdf#page=8",
        "https://content.dcf.ks.gov/ees/KEESM/Robo10-24/Robo_10_01_24/keesm13000.htm",
        "https://content.dcf.ks.gov/ees/KEESM/Robo01-26/Robo_01_01_26/keesm13000.htm",
        "https://content.dcf.ks.gov/ees/KEESM/Robo10-24/Robo_10_01_24/keesm13300.htm",
        "https://content.dcf.ks.gov/ees/KEESM/Robo01-26/Robo_01_01_26/keesm13300.htm",
    )
    defined_for = StateCode.KS

    def formula(spm_unit, period, parameters):
        income = spm_unit("ks_liheap_countable_income", period)
        limit = spm_unit("ks_liheap_income_limit", period)
        return income <= limit
