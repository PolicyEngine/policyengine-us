from policyengine_us.model_api import *


class md_tca_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Maryland TCA income eligible"
    definition_period = MONTH
    defined_for = StateCode.MD
    reference = "https://dsd.maryland.gov/regulations/Pages/07.03.03.13.aspx"

    def formula(spm_unit, period, parameters):
        # Per COMAR 07.03.03.13, eligibility is based on comparing
        # countable income to the grant standard
        countable_income = spm_unit("md_tca_countable_income", period)
        grant_standard = spm_unit("md_tca_maximum_benefit", period)
        return countable_income <= grant_standard
