from policyengine_us.model_api import *


class tx_tanf_countable_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Texas TANF countable unearned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.hhs.texas.gov/handbooks/texas-works-handbook/a-1340-income-limits",
        "https://www.law.cornell.edu/regulations/texas/1-TAC-372-605",
    )
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        gross_unearned_person = person("tx_tanf_gross_unearned_income", period)

        return spm_unit.sum(gross_unearned_person)
