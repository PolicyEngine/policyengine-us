from policyengine_us.model_api import *


class tx_fpp_countable_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Texas Family Planning Program countable unearned income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/regulations/texas/1-Tex-Admin-Code-SS-382-109",
        "https://www.hhs.texas.gov/sites/default/files/documents/fpppm-9000-definitions-of-income.pdf#page=2",
    )
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.tx.fpp.income
        unearned = add(spm_unit, period, p.sources.unearned)
        child_support = add(spm_unit, period, ["child_support_received"])
        annual_disregard = p.child_support_disregard * MONTHS_IN_YEAR
        return unearned + max_(child_support - annual_disregard, 0)
