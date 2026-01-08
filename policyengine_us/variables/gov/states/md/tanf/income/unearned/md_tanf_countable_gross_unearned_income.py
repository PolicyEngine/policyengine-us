from policyengine_us.model_api import *


class md_tanf_countable_gross_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Maryland TANF countable gross unearned income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MD
    reference = "https://dhs.maryland.gov/documents/Manuals/Temporary-Cash-Assistance-Manual/0900-Financial-Eligibility/0903%20Unearned%20Income%2011.22.doc"

    def formula(spm_unit, period, parameters):
        return spm_unit("md_tanf_gross_unearned", period)
