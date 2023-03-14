from policyengine_us.model_api import *


class co_tanf_need_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Colorado TANF need standard"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CO

    def formula(spm_unit, period, parameters):
        # Get number of children and adults in SPM unit.
        children = spm_unit("co_tanf_count_children", period)
        adults = spm_unit("spm_unit_count_adults", period)
        # Cap them at the maximum specified in the tables.
        capped_children = min_(children, 10).astype(int)
        capped_adults = min_(adults, 2).astype(int)
        # Calculate additional children beyond the maximum in tables.
        additional_children = children - capped_children
        # Get the relevant part of the parameter tree.
        p = parameters(period).gov.states.co.cdhs.tanf.need_standard
        # Look up the main need standard for the number of adults and (capped)
        # children.
        base = p.main[capped_adults][capped_children]
        # Add the additional need standard for the additional children.
        additional_need_standard = p.additional_child * additional_children
        monthly = base + additional_need_standard
        # Return annual value.
        return monthly * MONTHS_IN_YEAR
