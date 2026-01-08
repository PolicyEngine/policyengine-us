from policyengine_us.model_api import *


class md_tanf_maximum_benefit(Variable):
    value_type = float
    entity = SPMUnit
    label = "Maryland TANF maximum benefit"
    unit = USD
    definition_period = YEAR
    defined_for = "md_tanf_eligible"
    reference = "https://dhs.maryland.gov/documents/Manuals/Temporary-Cash-Assistance-Manual/0900-Financial-Eligibility/0908%20Grant%20Determination%20rev%2011.22.doc"

    def formula(spm_unit, period, parameters):
        people = spm_unit("spm_unit_size", period)
        p = parameters(period).gov.states.md.tanf.maximum_benefit
        max_size = p.max_unit_size
        capped_people = min_(people, max_size).astype(int)
        additional_people = people - capped_people
        base = p.main[capped_people]
        additional_maximum_benefit = p.additional * additional_people
        monthly = base + additional_maximum_benefit
        return monthly * MONTHS_IN_YEAR
