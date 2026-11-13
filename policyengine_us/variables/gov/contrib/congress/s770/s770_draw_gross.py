from policyengine_us.model_api import *


class s770_draw_gross(Variable):
    value_type = float
    entity = Person
    label = "Actual gross owners draw for S.770 interaction"
    documentation = "Integration hook for actual, floor-accepted owners draw under a future SECA reform. Supply actual gross draw, not planned or phase-in-rejected profits. This input classifies income only and does not itself impose SECA."
    unit = USD
    definition_period = YEAR
    reference = "https://www.congress.gov/bill/119th-congress/senate-bill/770/text"
