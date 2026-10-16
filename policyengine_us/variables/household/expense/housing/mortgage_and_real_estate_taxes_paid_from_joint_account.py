from policyengine_us.model_api import *


class mortgage_and_real_estate_taxes_paid_from_joint_account(Variable):
    value_type = bool
    entity = MaritalUnit
    label = "Mortgage interest and real estate taxes paid from a joint account"
    documentation = "Whether a married couple paid the home mortgage interest and real estate taxes they owe jointly from a joint account. North Carolina then shares its mortgage and property tax cap between spouses filing separately by income rather than by the amount each paid."
    definition_period = YEAR
    default_value = False
    reference = "https://www.ncleg.gov/EnactedLegislation/Statutes/HTML/BySection/Chapter_105/GS_105-153.5.html"
