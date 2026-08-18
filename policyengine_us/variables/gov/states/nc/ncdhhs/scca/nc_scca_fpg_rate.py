from policyengine_us.model_api import *


class nc_scca_fpg_rate(Variable):
    value_type = float
    entity = Person
    label = "North Carolina Subsidized Child Care Assistance (SCCA) program income limit as a share of the federal poverty level for this child"
    reference = "https://policies.ncdhhs.gov/wp-content/uploads/FINAL-Chapter-7-Family-definition-and-determining-income-eligibility-08-05-24.pdf#page=2"
    definition_period = YEAR
    defined_for = StateCode.NC

    def formula(person, period, parameters):
        # Chapter 7, Section II.A: income eligibility is compared per child to
        # 200% FPL for children ages 0-5 and all children with special needs,
        # and to 133% FPL for children ages 6-12 without special needs.
        p = parameters(period).gov.states.nc.ncdhhs.scca.entry.fpg_limit
        is_school_age = person("nc_scca_is_school_age", period)
        is_disabled = person("is_disabled", period)
        return where(~is_school_age | is_disabled, p.preschool, p.school_age)
