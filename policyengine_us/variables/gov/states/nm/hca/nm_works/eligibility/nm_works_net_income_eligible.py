from policyengine_us.model_api import *


class nm_works_net_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "New Mexico Works net income eligible"
    definition_period = MONTH
    reference = "https://www.srca.nm.gov/parts/title08/08.102.0520.html"
    defined_for = StateCode.NM

    def formula(spm_unit, period, parameters):
        # Per 8.102.520.11 NMAC, countable income must be less than
        # the standard of need (payment standard)
        countable_income = spm_unit("nm_works_countable_income", period)
        payment_standard = spm_unit("nm_works_maximum_benefit", period)
        return countable_income <= payment_standard
