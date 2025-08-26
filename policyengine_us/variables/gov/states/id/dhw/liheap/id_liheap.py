from policyengine_us.model_api import *


class id_liheap(Variable):
    value_type = float
    entity = SPMUnit
    label = "Idaho LIHEAP"
    unit = USD
    definition_period = YEAR
    defined_for = "id_liheap_eligible"
    reference = "https://healthandwelfare.idaho.gov/services-programs/financial-assistance/home-heating-and-utility-assistance/"
    documentation = "Total Idaho Low Income Home Energy Assistance Program benefit"

    def formula(spm_unit, period, parameters):
        # Sum heating and crisis assistance
        heating_assistance = spm_unit("id_liheap_heating_assistance", period)
        crisis_assistance = spm_unit("id_liheap_crisis_assistance", period)
        
        return heating_assistance + crisis_assistance