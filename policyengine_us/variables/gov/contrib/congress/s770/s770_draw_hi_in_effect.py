from policyengine_us.model_api import *


class s770_draw_hi_in_effect(Variable):
    value_type = bool
    entity = Person
    label = "Actual owners draw is subject to uncapped SECA HI"
    documentation = "Integration hook: true only where the actual gross draw supplied in s770_draw_gross is subject to uncapped SECA HI. Exclude the full gross draw in that case; otherwise exclude only the gross equivalent of its capped OASDI base. Undrawn and floor-rejected amounts stay in active income."
    definition_period = YEAR
    reference = "https://www.congress.gov/bill/119th-congress/senate-bill/770/text"
