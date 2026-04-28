from policyengine_us.model_api import *


class md_paa_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Maryland PAA eligible"
    definition_period = MONTH
    defined_for = StateCode.MD
    reference = (
        "https://dhs.maryland.gov/documents/FIA/Manuals/Public%20Assistance%20to%20Adults%20%28PAA%29%20Manual/PAA%20300%20Technical%20Eligibility%20rev%2011.22.docx",
        "https://www.law.cornell.edu/regulations/maryland/COMAR-07-03-07-03",
    )

    def formula(person, period, parameters):
        # PAA Manual §300.2 requires actual SSI receipt, not just SSI eligibility.
        receives_ssi = person("ssi", period) > 0
        living_arrangement = person("md_paa_living_arrangement", period)
        in_facility = living_arrangement != living_arrangement.possible_values.NONE
        return receives_ssi & in_facility
