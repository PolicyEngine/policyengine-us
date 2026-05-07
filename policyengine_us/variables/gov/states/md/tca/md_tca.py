from policyengine_us.model_api import *


class md_tca(Variable):
    value_type = float
    entity = SPMUnit
    label = "Maryland Temporary Cash Assistance"
    unit = USD
    definition_period = MONTH
    defined_for = "md_tca_eligible"
    reference = "https://dsd.maryland.gov/regulations/Pages/07.03.03.17.aspx"

    def formula(spm_unit, period, parameters):
        grant_standard = spm_unit("md_tca_maximum_benefit", period)
        countable_income = spm_unit("md_tca_countable_income", period)
        benefit = max_(grant_standard - countable_income, 0)
        return min_(benefit, grant_standard)
