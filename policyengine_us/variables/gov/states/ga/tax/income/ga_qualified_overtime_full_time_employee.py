from policyengine_us.model_api import *


class ga_qualified_overtime_full_time_employee(Variable):
    value_type = bool
    entity = Person
    label = "Full-time employee for the Georgia qualified overtime exclusion"
    documentation = (
        "Whether the person is a full-time employee under O.C.G.A. § "
        "48-7-27(a)(16)(A). The formula compares usual weekly hours with the "
        "full-time threshold, so a record without hours is not full-time. Set "
        "this variable directly when full-time status is known and hours "
        "are not."
    )
    definition_period = YEAR
    defined_for = StateCode.GA
    reference = (
        "https://www.legis.ga.gov/api/legislation/document/20252026/249080#page=6"
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ga.tax.income.agi.exclusions.overtime
        # Usual hours in the weeks worked, so a part-year full-time employee
        # stays full-time. Like other eligibility tests, this reads hours
        # before labor supply responses, which do not change eligibility.
        hours = person("weekly_hours_worked_before_lsr", period)
        return hours >= p.full_time_weekly_hours
