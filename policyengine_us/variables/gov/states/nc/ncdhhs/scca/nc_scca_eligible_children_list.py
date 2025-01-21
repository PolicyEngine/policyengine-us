from policyengine_us.model_api import *

# can I take all the qualified children out and put them into a list and saved for future use?
class nc_scca_eligible_children_list(Variable):
    value_type = list # ??
    entity = SPMUnit
    label = "Number of children eligible for North Carolina Subsidized Child Care Assistance program"
    definition_period = MONTH
    defined_for = StateCode.NC
    
    def formula(spm_unit, period, parameters):
        eligible_children = []
        for member in spm_unit.members:
            age = member("age", period.this_year) 

            # child < 13 or disabled child < 17 to be eligible
            is_disabled = member("is_disabled", period.this_year)

            # need to use params here
            if age <= 5: 
                eligible_children.append(member)
            elif age >= 6 & age <= 12:
                eligible_children.append(member)
            elif (age >= 6 & age <= 17) & is_disabled:
                eligible_children.append(member)

        return eligible_children   
