from policyengine_us.model_api import *


class MSPCategory(Enum):
    NONE = "None"
    QMB = "Qualified Medicare Beneficiary"
    SLMB = "Specified Low-Income Medicare Beneficiary"
    QI = "Qualifying Individual"


class msp_category(Variable):
    value_type = Enum
    possible_values = MSPCategory
    default_value = MSPCategory.NONE
    entity = Person
    label = "Medicare Savings Program category"
    definition_period = MONTH
    documentation = (
        "The MSP category for which a person qualifies. "
        "QMB is most generous, then SLMB, then QI."
    )
    reference = "https://www.cms.gov/medicare/costs/medicare-savings-programs"

    def formula(person, period, parameters):
        is_qmb = person("is_qmb_eligible", period)
        is_slmb = person("is_slmb_eligible", period)
        is_qi = person("is_qi_eligible", period)
        # Return highest category person qualifies for
        return select(
            [is_qmb, is_slmb, is_qi],
            [MSPCategory.QMB, MSPCategory.SLMB, MSPCategory.QI],
            default=MSPCategory.NONE,
        )
