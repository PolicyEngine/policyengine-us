from policyengine_us.model_api import *


class il_schedule_m_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "IL Schedule M additions"
    unit = USD
    definition_period = YEAR
    reference = "https://www2.illinois.gov/rev/forms/incometax/Documents/currentyear/individual/il-1040-schedule-m.pdf"
