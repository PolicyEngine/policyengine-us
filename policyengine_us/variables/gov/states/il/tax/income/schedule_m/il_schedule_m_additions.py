from policyengine_us.model_api import *


class il_schedule_m_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "IL Schedule M additions"
    unit = USD
    definition_period = YEAR
    reference = "https://taxarchive.illinois.gov/content/dam/soi/en/web/taxarchive/forms/income-tax/2019/individual/il-1040-schedule-m.pdf"
    defined_for = StateCode.IL
