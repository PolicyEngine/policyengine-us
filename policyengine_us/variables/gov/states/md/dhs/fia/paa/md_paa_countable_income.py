from policyengine_us.model_api import *


class md_paa_countable_income(Variable):
    value_type = float
    entity = Person
    label = "Maryland PAA countable income"
    unit = USD
    definition_period = MONTH
    defined_for = "md_paa_eligible"
    reference = (
        "https://dhs.maryland.gov/documents/FIA/Manuals/Public%20Assistance%20to%20Adults%20%28PAA%29%20Manual/PAA%20900%20Calculation%20of%20Benefits%20rev%2011.22.docx",
        "https://www.law.cornell.edu/regulations/maryland/COMAR-07-03-07-09",
    )
    adds = [
        "md_paa_countable_earned_income",
        "md_paa_countable_unearned_income",
    ]
