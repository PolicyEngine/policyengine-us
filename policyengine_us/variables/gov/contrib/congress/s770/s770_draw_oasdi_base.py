from policyengine_us.model_api import *


class s770_draw_oasdi_base(Variable):
    value_type = float
    entity = Person
    label = "Owners draw net earnings actually taxed by OASDI"
    documentation = "Integration hook for adjusted owners draw after wages, existing SE earnings and the applicable cap room. With draw HI off, only this amount divided by the SE netting factor is excluded from active income; above-room profits stay in the active base. This input does not itself impose SECA."
    unit = USD
    definition_period = YEAR
    reference = "https://www.congress.gov/bill/119th-congress/senate-bill/770/text"
