from policyengine_us.model_api import *


class md_paa_total_cost_of_care(Variable):
    value_type = float
    entity = Person
    label = "Maryland PAA total cost of care"
    unit = USD
    definition_period = MONTH
    defined_for = "md_paa_eligible"
    reference = "https://dhs.maryland.gov/documents/FIA/Manuals/Public%20Assistance%20to%20Adults%20%28PAA%29%20Manual/PAA%20900%20Calculation%20of%20Benefits%20rev%2011.22.docx"
    adds = ["md_paa_provider_rate", "md_paa_personal_needs_allowance"]
