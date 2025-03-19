from policyengine_us.model_api import *


class total_misc_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Total miscellaneous deductions subject to the AGI floor"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/67#b"

    adds = "gov.irs.deductions.itemized.misc.sources"
