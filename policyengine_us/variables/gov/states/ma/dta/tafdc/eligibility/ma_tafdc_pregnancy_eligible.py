from policyengine_us.model_api import *


class ma_tafdc_pregnancy_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) due to income"
    definition_period = YEAR
    reference = "https://www.mass.gov/how-to/transitional-aid-to-families-with-dependent-children-tafdc"
    defined_for = StateCode.MA

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        is_pregnant = person("is_pregnant", period)
        age = person("age", period)
        current_pregnancy_month = person("current_pregnancy_month", period)
        p = parameters(period).gov.states.ma.dta.tafdc.eligibility
        young_pregnancy = age < p.pregnancy_age
        months_eligible = where(
            young_pregnancy, True, current_pregnancy_month >= p.pregnancy_month
        )
        return spm_unit.any(is_pregnant & months_eligible)
       
        # young_pregnancy_eligible = is_pregnant & young_pregnancy & is_in_k12_school or k12 graduate(Teen Parent School Attendance)
        
        # months_eligible = is_pregnant & current_pregnancy_month >= p.pregnancy_month
        # return spm_unit.any(young_pregnancy_eligible | months_eligible)