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
    reference = (
        "https://www.medicare.gov/basics/costs/help/medicare-savings-programs",
        "https://www.law.cornell.edu/cfr/text/42/435.121",
    )

    def formula(person, period, parameters):
        qmb = person("is_qmb_eligible", period)
        slmb = person("is_slmb_eligible", period)
        qi = person("is_qi_eligible", period)

        # Priority: QMB > SLMB > QI (QMB is most comprehensive)
        return select(
            [qmb, slmb, qi],
            [MSPCategory.QMB, MSPCategory.SLMB, MSPCategory.QI],
            default=MSPCategory.NONE,
        )
