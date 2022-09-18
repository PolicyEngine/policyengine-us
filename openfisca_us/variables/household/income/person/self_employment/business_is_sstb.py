from openfisca_us.model_api import *


class business_is_sstb(Variable):
    value_type = bool
    entity = Person
    label = "Business is SSTB"
    unit = USD
    documentation = "Whether all income from self-employment, partnerships and S-corporations is from qualified businesses. A qualified trade or business is any specified service trade or business, or employment. The list of specified service trades can be found at https://www.law.cornell.edu/uscode/text/26/1202#e_3_A."
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/199A#d_1"
