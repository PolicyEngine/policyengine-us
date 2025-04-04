from policyengine_us.model_api import *


class dc_child_care_income_requirement_waived(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Income requirement waived for DC Childcare Subsidy"
    definition_period = YEAR
    defined_for = StateCode.DC
    reference = "https://osse.dc.gov/sites/default/files/dc/sites/osse/publication/attachments/DC%20Child%20Care%20Subsidy%20Program%20Policy%20Manual.pdf"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.dc.dhs.child_care.special_categories
        person = spm_unit.members

        # Only full waiver categories get income requirement waived
        # Children under protective services
        protective_services = False  # Placeholder

        # Children of adults with disabilities
        is_adult = ~person("is_child", period)
        is_disabled = person("is_disabled", period)
        adult_with_disability = spm_unit.any(is_adult & is_disabled)

        # Children experiencing homelessness
        is_homeless = False  # Placeholder

        # Children of teen parents
        is_parent = False  # Placeholder
        is_teen = person("age", period) < 20
        teen_parent = spm_unit.any(is_parent & is_teen)

        # Children in Head Start/Early Head Start/QIN
        in_head_start = False  # Placeholder

        # Children in families experiencing domestic violence
        domestic_violence = False  # Placeholder

        # Combine full waiver categories
        full_waiver = (
            protective_services
            | adult_with_disability
            | is_homeless
            | teen_parent
            | in_head_start
            | domestic_violence
        )

        return full_waiver
