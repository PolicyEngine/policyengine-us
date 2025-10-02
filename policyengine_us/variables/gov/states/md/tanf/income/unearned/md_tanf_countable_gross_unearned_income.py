from policyengine_us.model_api import *

# reference: https://dhs.maryland.gov/documents/Manuals/Temporary-Cash-Assistance-Manual/0900-Financial-Eligibility/0903%20Unearned%20Income%2011.22.doc


class md_tanf_countable_gross_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Maryland TANF countable gross unearned income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MD

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        gross_unearned = spm_unit("md_tanf_gross_unearned", period)
        child_support = spm_unit.sum(person("child_support_received", period))
        enrolled = spm_unit("is_tanf_enrolled", period)

        return gross_unearned + enrolled * child_support
