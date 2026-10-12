from policyengine_us.model_api import *


class ms_wd_fpg(Variable):
    value_type = float
    entity = Person
    label = "Mississippi Working Disabled monthly federal poverty guideline"
    unit = USD
    definition_period = MONTH
    reference = "https://medicaid.ms.gov/wp-content/uploads/2025/07/Chapter-400-ABD-and-MAGI-Eligibility-Criteria-and-Budgeting.-Revised-July-2025v2.pdf#page=32"
    defined_for = StateCode.MS

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs.fpg
        state_group = person.household("state_group_str", period)
        unit_size = person.marital_unit.nb_persons()
        annual_fpg = (
            p.first_person[state_group]
            + (unit_size - 1) * p.additional_person[state_group]
        )
        return annual_fpg / MONTHS_IN_YEAR
