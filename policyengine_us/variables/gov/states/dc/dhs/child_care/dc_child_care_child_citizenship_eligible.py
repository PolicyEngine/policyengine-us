from policyengine_us.model_api import *


class dc_child_care_child_citizenship_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Child meets DC Childcare Subsidy citizenship requirements"
    definition_period = YEAR
    defined_for = StateCode.DC
    reference = "https://osse.dc.gov/sites/default/files/dc/sites/osse/publication/attachments/DC%20Child%20Care%20Subsidy%20Program%20Policy%20Manual.pdf"

    def formula(person, period, parameters):
        # Check if person is a child
        is_child = person("is_child", period)

        # Get citizenship requirements
        p = parameters(
            period
        ).gov.states.dc.dhs.child_care.citizenship_requirements

        # Check citizenship status
        immigration_status = person("immigration_status", period)
        status = immigration_status.possible_values

        citizen = immigration_status == status.CITIZEN
        legal_permanent_resident = (
            immigration_status == status.LEGAL_PERMANENT_RESIDENT
        )
        qualified_alien = (
            immigration_status
            == status.REFUGEE | immigration_status
            == status.ASYLUM | legal_permanent_resident
        )

        eligible_status = citizen | qualified_alien

        # Only children need to meet citizenship requirements
        return is_child & eligible_status
