from policyengine_us.model_api import *

# reference: https://dhs.maryland.gov/documents/Manuals/Temporary-Cash-Assistance-Manual/0900-Financial-Eligibility/0903%20Unearned%20Income%2011.22.doc


class md_tanf_gross_unearned(Variable):
    value_type = float
    entity = SPMUnit
    label = "Maryland TANF countable gross unearned income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MD

    adds = "gov.states.md.tanf.income.sources.unearned"
