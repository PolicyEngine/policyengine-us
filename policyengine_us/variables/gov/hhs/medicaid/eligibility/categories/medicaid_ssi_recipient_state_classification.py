from policyengine_us.model_api import *


class MedicaidSSIRecipientStateClassification(Enum):
    SECTION_1634 = "1634"
    SSI_CRITERIA = "SSI criteria"
    SECTION_209B = "209(b)"
    UNKNOWN = "Unknown"


class medicaid_ssi_recipient_state_classification(Variable):
    value_type = Enum
    possible_values = MedicaidSSIRecipientStateClassification
    default_value = MedicaidSSIRecipientStateClassification.UNKNOWN
    entity = Person
    label = "Medicaid SSI-recipient state classification"
    definition_period = YEAR
    reference = "https://secure.ssa.gov/apps10/poms.nsf/lnx/0501715010"

    def formula(person, period, parameters):
        state = person.household("state_code_str", period)
        classification = parameters(
            period
        ).gov.hhs.medicaid.eligibility.categories.ssi_recipient.classification

        return select(
            [
                classification.section_1634[state].astype(bool),
                classification.ssi_criteria[state].astype(bool),
                classification.section_209b[state].astype(bool),
            ],
            [
                MedicaidSSIRecipientStateClassification.SECTION_1634,
                MedicaidSSIRecipientStateClassification.SSI_CRITERIA,
                MedicaidSSIRecipientStateClassification.SECTION_209B,
            ],
            default=MedicaidSSIRecipientStateClassification.UNKNOWN,
        )
