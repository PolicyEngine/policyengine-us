from policyengine_us.model_api import *


class la_ccap_total_copay(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    label = "Louisiana CCAP total monthly co-payment"
    unit = USD
    reference = "https://www.louisianabelieves.com/docs/default-source/early-childhood/ccap-sliding-fee-scale.pdf"
    defined_for = "la_ccap_eligible"

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        # The sliding fee scale co-payment applies per child per paid day;
        # waivers zero it through la_ccap_daily_copay.
        daily_copay = spm_unit("la_ccap_daily_copay", period)
        monthly_days = spm_unit.sum(person("la_ccap_monthly_days", period))
        return daily_copay * monthly_days
