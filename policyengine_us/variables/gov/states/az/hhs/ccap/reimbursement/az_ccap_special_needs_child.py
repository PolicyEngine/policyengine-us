from policyengine_us.model_api import *


class az_ccap_special_needs_child(Variable):
    value_type = bool
    entity = Person
    label = "Arizona Child Care Assistance Program special needs child"
    definition_period = MONTH
    defined_for = StateCode.AZ
    reference = (
        "https://des.az.gov/sites/default/files/dl/CCA-1210B.pdf#page=6",
        "https://des.az.gov/sites/default/files/dl/CCA-1210B.pdf#page=14",
    )

    def formula(person, period, parameters):
        # CCA-1210B item 14: a child with special needs has a documented disability
        # via an IFSP (AzEIP / IDEA Part C), an IEP (special education / IDEA Part B),
        # an ISP (Division of Developmental Disabilities), or a 504 Plan. We
        # approximate those pathways with the available person-level flags.
        has_documented_disability = (
            person("is_disabled", period.this_year)
            | person("has_individualized_education_program", period.this_year)
            | person("has_developmental_delay", period.this_year)
        )
        return person("az_ccap_eligible_child", period) & has_documented_disability
