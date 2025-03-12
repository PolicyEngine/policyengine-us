from policyengine_us.model_api import *


class ma_mbta_enrolled_in_applicable_programs(Variable):
    value_type = bool
    entity = Person
    label = "Enrolled in applicable programs to receive the Massachusetts Bay Transportation Authority income-eligible reduced fare program"
    definition_period = YEAR
    defined_for = StateCode.MA
    reference = "https://www.mbta.com/fares/reduced/income-eligible"

    adds = "gov.states.ma.dot.mbta.income_eligible_reduced_fares.applicable_programs"
