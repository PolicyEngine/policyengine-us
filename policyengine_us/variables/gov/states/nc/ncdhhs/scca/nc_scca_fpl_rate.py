from policyengine_us.model_api import *


class nc_scca_fpl_rate(Variable):
    value_type = float
    entity = SPMUnit
    label = "Child age eligibility for North Carolina Subsidized Child Care Assistance (SCCA) program"
    reference = "https://ncchildcare.ncdhhs.gov/Portals/0/documents/pdf/A/ACF-118_CCDF_FFY_2022-2024_For_North_Carolina_Amendment_1.pdf?ver=C9YfIUPAFekeBA3I1mN8aA%3d%3d#page=83"
    definition_period = MONTH
    defined_for = StateCode.NC

    # question: 
    # is this the right way to find the younest child's age,
    # and if the younest one is over 6 and under 17 and disabled
    def formula(spm_unit, period, parameters):
        # entry income eligible depends on the youngest child's age, 
        # 0-5, or with specail needs or court supervision, 200% fpl
        # 6-12, 133%
        p = parameters(period).gov.states.nc.scca

        # get the youngest child's age
        person = spm_unit.members
        age = person("age", period)
        min_age = spm_unit.min(age)

        # child < 13 or disabled child < 17 to be eligible
        is_disabled = person("is_disabled", period.this_year)

        if min_age <= 5 | (min_age >= 6 & min_age <= 17) & is_disabled: 
            categorized_age = 5
        elif min_age >= 6 & age <= 12:
            categorized_age = 6

        rate = p.entry.income_rate_by_child_age.calc(categorized_age)
        return rate
