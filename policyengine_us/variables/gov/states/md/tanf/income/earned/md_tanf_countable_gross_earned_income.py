from policyengine_us.model_api import *

# reference: https://dhs.maryland.gov/documents/Manuals/Temporary-Cash-Assistance-Manual/0900-Financial-Eligibility/0902%20TCA%20Earned%20Income%20rev%2011.22.doc


class md_tanf_countable_gross_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Maryland TANF countable gross earned income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MD

    adds = "gov.states.md.tanf.income.sources.earned"
