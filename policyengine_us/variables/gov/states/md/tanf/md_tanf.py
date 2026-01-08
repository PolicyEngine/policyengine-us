from policyengine_us.model_api import *


class md_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "Maryland Temporary Cash Assistance"
    unit = USD
    definition_period = MONTH
    defined_for = "md_tanf_eligible"
    reference = "https://dsd.maryland.gov/regulations/Pages/07.03.03.17.aspx"

    def formula(spm_unit, period, parameters):
        grant_standard = spm_unit("md_tanf_maximum_benefit", period)
        income = spm_unit("md_tanf_net_countable_income", period)
        return max_(grant_standard - income, 0)
