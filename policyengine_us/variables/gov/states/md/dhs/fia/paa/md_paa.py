from policyengine_us.model_api import *


class md_paa(Variable):
    value_type = float
    entity = Person
    label = "Maryland Public Assistance to Adults"
    unit = USD
    definition_period = MONTH
    defined_for = "md_paa_eligible"
    reference = (
        "https://dhs.maryland.gov/documents/FIA/Manuals/Public%20Assistance%20to%20Adults%20%28PAA%29%20Manual/PAA%20900%20Calculation%20of%20Benefits%20rev%2011.22.docx",
        "https://www.law.cornell.edu/regulations/maryland/COMAR-07-03-07-09",
    )

    def formula(person, period, parameters):
        total_cost_of_care = person("md_paa_total_cost_of_care", period)
        countable_income = person("md_paa_countable_income", period)
        return max_(total_cost_of_care - countable_income, 0)
