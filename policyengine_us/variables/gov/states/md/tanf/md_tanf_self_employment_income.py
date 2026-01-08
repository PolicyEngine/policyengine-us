from policyengine_us.model_api import *


class md_tanf_self_employment_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Maryland TANF self-employment income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MD
    reference = "https://dhs.maryland.gov/documents/Manuals/Temporary-Cash-Assistance-Manual/0900-Financial-Eligibility/0902%20TCA%20Earned%20Income%20rev%2011.22.doc"

    adds = "gov.irs.tax.self_employment.taxable_self_employment_income"
