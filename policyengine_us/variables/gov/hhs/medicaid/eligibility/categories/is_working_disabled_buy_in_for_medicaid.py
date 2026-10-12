from policyengine_us.model_api import *


class is_working_disabled_buy_in_for_medicaid(Variable):
    value_type = bool
    entity = Person
    label = "Working disabled Medicaid Buy-In"
    documentation = (
        "Whether this person qualifies for Medicaid through a working disabled "
        "Buy-In pathway. Currently modeled pathways are California's 250% "
        "Working Disabled Program, Illinois Health Benefits for Workers "
        "with Disabilities, and Mississippi's Working Disabled program."
    )
    definition_period = YEAR
    reference = (
        "https://www.dhcs.ca.gov/services/working-disabled-program/",
        "https://hfs.illinois.gov/medicalprograms/hbwd.html",
        "https://medicaid.ms.gov/medicaid-coverage/who-qualifies-for-coverage/working-disabled/",
    )

    def formula(person, period, parameters):
        ca_wdp_eligible = person("ca_wdp_eligible", period)
        il_hbwd_eligible = person("il_hbwd_eligible", period.first_month)
        ms_wd_eligible = person("ms_wd_eligible", period.first_month)
        return ca_wdp_eligible | il_hbwd_eligible | ms_wd_eligible
