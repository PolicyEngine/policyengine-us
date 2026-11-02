from policyengine_us.model_api import *


class vt_aabd_ep_additional_countable_income(Variable):
    value_type = float
    entity = Person
    label = "Vermont Essential Person income outside the marital group"
    definition_period = MONTH
    unit = USD
    # PDF pages 48-51
    reference = "https://outside.vermont.gov/dept/DCF/Shared%20Documents/ESD/Rules/2700-AABD.pdf#page=48"
    documentation = "Verified net income of a nonspouse essential person and any parental allocation. Apply the Reach Up exclusions, dependent proration, worker expense allowance and any unused share of the single group general exclusion before entering this amount; do not duplicate the marital group income."
