from policyengine_us.model_api import *


class ca_riv_share_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Riverside County Sharing Households Assist Riverside's Energy program (SHARE) countable income"
    definition_period = YEAR
    defined_for = "in_riv"
    reference = "https://riversideca.gov/utilities/residents/assistance-programs/share-english"

    adds = "gov.local.ca.riv.cap.share.countable_income.sources"
