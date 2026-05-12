from policyengine_us.model_api import *


class wa_pfml_max_leave_weeks(Variable):
    value_type = float
    entity = Person
    label = "Washington PFML maximum leave weeks"
    documentation = (
        "Maximum Washington Paid Family and Medical Leave duration in weeks "
        "for the selected leave type."
    )
    unit = "week"
    definition_period = YEAR
    defined_for = "wa_pfml_eligible"
    reference = (
        "https://app.leg.wa.gov/rcw/default.aspx?cite=50A.15.020",
        "https://app.leg.wa.gov/rcw/default.aspx?cite=50A.15.010",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.wa.pfml
        leave_type = person("wa_pfml_leave_type", period)
        leave_type_values = leave_type.possible_values
        return select(
            [
                leave_type == leave_type_values.FAMILY,
                leave_type == leave_type_values.MEDICAL,
                leave_type == leave_type_values.COMBINED,
                leave_type == leave_type_values.MEDICAL_WITH_PREGNANCY_INCAPACITY,
                leave_type == leave_type_values.COMBINED_WITH_PREGNANCY_INCAPACITY,
            ],
            [
                p.duration.family_leave_weeks,
                p.duration.medical_leave_weeks,
                p.duration.combined_max_weeks,
                p.duration.medical_leave_weeks_with_pregnancy_incapacity,
                p.duration.combined_max_weeks_with_pregnancy_incapacity,
            ],
            default=0,
        )
