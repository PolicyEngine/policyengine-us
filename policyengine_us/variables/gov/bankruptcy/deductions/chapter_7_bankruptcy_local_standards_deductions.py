from policyengine_us.model_api import *


class chapter_7_bankruptcy_local_standards_deductions(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Local standards deduction"
    definition_period = MONTH
    reference = "https://www.cacb.uscourts.gov/sites/cacb/files/documents/forms/122A2.pdf#page=3"

    def formula(spm_unit, period, parameters):
        # Housing and utilities + vehicle operation (owned or lease, public transportation)
        p = parameters(
            period
        ).gov.bankruptcy.local_standards
        size = spm_unit("spm_unit_size", period)
        state = spm_unit.household("state_code_str", period)
        insurance_and_operating_allowance = p.housing_and_utilities.insurance_and_operating[state][size]
        
        mortgage_or_rent_allowance = p.housing_and_utilities.mortgage_or_rent[state][size]
        monthly_housing_payment = add(spm_unit,period,["housing_cost"])/MONTHS_IN_YEAR
        net_mortgage_or_rent_expense = max_(mortgage_or_rent_allowance - monthly_housing_payment,0)
        
        ## vehciel opertating expense
        
        public_transportation_allowance = p.vehicle_operation.public_transportation
        public_transportation_expense = add(spm_unit,period,["public_transportation_expense"])
        net_public_transportation_expense = max_(public_transportation_allowance - public_transportation_expense,0)
        
        return net_mortgage_or_rent_expense + net_public_transportation_expense