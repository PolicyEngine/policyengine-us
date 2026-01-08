from policyengine_us.model_api import *


class md_tanf_gross_unearned(Variable):
    value_type = float
    entity = SPMUnit
    label = "Maryland TANF gross unearned income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MD
    reference = "https://dhs.maryland.gov/documents/Manuals/Temporary-Cash-Assistance-Manual/0900-Financial-Eligibility/0903%20Unearned%20Income%2011.22.doc"

    adds = "gov.states.md.tanf.income.sources.unearned"
