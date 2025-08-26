from policyengine_us.model_api import *


class id_liheap_crisis_assistance(Variable):
    value_type = float
    entity = SPMUnit
    label = "Idaho LIHEAP crisis assistance"
    unit = USD
    definition_period = YEAR
    defined_for = "id_liheap_eligible"
    reference = "https://liheapch.acf.gov/profiles/Idaho.htm"
    documentation = "Crisis assistance for households facing energy emergencies"

    def formula(spm_unit, period, parameters):
        # Get parameters
        p = parameters(period).gov.states.id.dhw.liheap.crisis_assistance
        
        # Crisis assistance is provided for energy emergencies
        # This is a placeholder - actual crisis determination would need
        # additional variables for shutoff notices, broken equipment, etc.
        
        # For now, return 0 as crisis assistance requires specific emergency conditions
        # This would need to be enhanced with actual crisis indicators
        return 0