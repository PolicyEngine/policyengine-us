from policyengine_us.model_api import *


class ne_child_care_subsidy_eligible_parent(Variable):
    value_type = bool
    entity = Person
    label = "Nebraska Child Care Subsidy program eligible parent"
    definition_period = MONTH
    reference = (
        "https://rules.nebraska.gov/api/fileStorage/GetAsByteArray/title-pdfs/Title_392.pdf/180#page=15",
        "https://dhhs.ne.gov/Child%20Care%20Documents/ACF-118%20CCDF%20FFY%202025-2027%20For%20Nebraska%20-%20APPROVED.pdf#page=17",
    )
    defined_for = StateCode.NE

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ne.dhhs.child_care_subsidy.income
        # Test each source independently so a business or farm loss cannot
        # erase positive wages when determining whether the caretaker works.
        employed = np.any(
            [person(source, period) > 0 for source in p.sources.earned],
            axis=0,
        )
        student = person("is_full_time_student", period.this_year)
        approved_activity = person.spm_unit(
            "meets_ccdf_activity_test", period.this_year
        )
        return employed | student | approved_activity
