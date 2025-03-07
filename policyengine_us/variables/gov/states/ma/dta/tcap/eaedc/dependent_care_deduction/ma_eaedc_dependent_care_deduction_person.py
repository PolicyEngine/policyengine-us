from policyengine_us.model_api import *


class ma_eaedc_dependent_care_deduction_person(Variable):
    value_type = float
    entity = Person
    label = "Massachusetts EAEDC dependent care deduction per person"
    unit = USD
    definition_period = YEAR
    defined_for = "ma_eaedc_dependent_care_deduction_person_eligible"
    reference = "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-275#(B)"

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.ma.dta.tcap.eaedc.deductions.dependent_care.maximum_deductions
        age = person("age", period)
        weekly_hours = person.spm_unit("spm_unit_weekly_hours_worked", period)
        # Calculate amount based on age and hours worked
        dependent_care_deduction_maximum_monthly = where(
            age < p.deduction_age_threshold,
            p.younger.calc(weekly_hours),
            p.older.calc(weekly_hours),
        )
        return dependent_care_deduction_maximum_monthly * MONTHS_IN_YEAR
