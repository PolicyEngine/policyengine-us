from policyengine_us.model_api import *


class wa_sfa_student_pathway_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Washington SFA student pathway eligible"
    definition_period = MONTH
    defined_for = StateCode.WA
    reference = (
        # WAC 388-400-0010(2)(c): SFA pathway for 19-20 year old students.
        "https://app.leg.wa.gov/wac/default.aspx?cite=388-400-0010",
        # WAC 388-404-0005(3): student definition for the SFA pathway.
        "https://app.leg.wa.gov/wac/default.aspx?cite=388-404-0005",
    )
    # WAC 388-404-0005(3)(a) extends SFA to 19-20 year olds with disabilities
    # receiving special education per RCW 28A.155.020. We do not separately
    # model that pathway at the moment; students still in K-12 special
    # education at ages 19-20 are typically captured by is_in_secondary_school.

    def formula(person, period, parameters):
        age = person("age", period.this_year)
        p = parameters(period).gov.states.wa.dshs.sfa.student_pathway
        in_age_range = p.age_eligible.calc(age)
        in_secondary = person("is_in_secondary_school", period.this_year)
        in_vocational = person("technical_institution_student", period.this_year)
        return in_age_range & (in_secondary | in_vocational)
