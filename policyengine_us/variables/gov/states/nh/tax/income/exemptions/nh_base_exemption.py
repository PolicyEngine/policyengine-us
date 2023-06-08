from policyengine_us.model_api import *


class nh_base_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Hampshire base exemption household level"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NH

    def formula(tax_unit, period, parameters):

        # get number of tax unit
        tax_unit_size = tax_unit("tax_unit_size", period) 

        # How can I use the person level base exemption for this household one?
        
        # I think the ADD function you mentioned is used in nh_total_exemptions.py, which adds all different 
        # typels of exemptions. 
        
        return 