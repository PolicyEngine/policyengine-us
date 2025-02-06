from policyengine_us.model_api import *


class nc_scca_fpl_rate(Variable):
    value_type = float
    entity = SPMUnit
    label = "Child age eligibility for North Carolina Subsidized Child Care Assistance (SCCA) program"
    reference = "https://ncchildcare.ncdhhs.gov/Portals/0/documents/pdf/A/ACF-118_CCDF_FFY_2022-2024_For_North_Carolina_Amendment_1.pdf?ver=C9YfIUPAFekeBA3I1mN8aA%3d%3d#page=83"
    definition_period = YEAR
    defined_for = StateCode.NC

    def formula(spm_unit, period, parameters):
        # entry income eligible depends on the youngest child's age, 
        # 0-5, or with specail needs, 200% fpl
        # 6-12, 133%
        p = parameters(period).gov.states.nc.ncdhhs.scca

        # Retrieve age and disability status for all members
        persons = spm_unit.members
        ages = persons("age", period)
        disabilities = persons("is_disabled", period)
        
        # get the youngest child's age
        min_age = min(ages)

        categorized_age = 6

        # Check if any child (6-16) is disabled
        if any(6 <= age < 17 and is_disabled for age, is_disabled in zip(ages, disabilities)):
            categorized_age = 5
        elif min_age <= 5:  
            categorized_age = 5
        elif 6 <= min_age <= 12:  
            categorized_age = 6      

        rate = p.entry.income_rate_by_child_age.calc(categorized_age)
        return rate
