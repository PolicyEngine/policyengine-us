from policyengine_us.model_api import *


class tx_liheap_has_young_child(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Texas LIHEAP household has young child"
    documentation = (
        "Determines if household has a child under the specified age threshold"
    )
    reference = "https://www.tdhca.texas.gov/sites/default/files/2023-10/FY2024-LIHEAP-State-Plan.pdf"
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.tx.tdhca.liheap

        # Get ages of all members
        person = spm_unit.members
        age = person("age", period)

        # Check if any member is under child age threshold
        # Use min_ to avoid .any() which breaks vectorization
        min_age = spm_unit.min(age)
        
        return min_age < p.child_age_threshold
