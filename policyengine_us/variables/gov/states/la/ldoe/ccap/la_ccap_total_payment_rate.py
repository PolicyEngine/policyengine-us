from policyengine_us.model_api import *


class la_ccap_total_payment_rate(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    label = "Louisiana CCAP total monthly payment rate"
    unit = USD
    reference = "https://www.doa.la.gov/media/043btqeh/28v165.docx"
    defined_for = "la_ccap_eligible"

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        # LAC 28:CLXV.515: the state maximum daily rate times the paid days
        # for each eligible child in care.
        daily_rate = person("la_ccap_daily_rate", period)
        monthly_days = person("la_ccap_monthly_days", period)
        return spm_unit.sum(daily_rate * monthly_days)
