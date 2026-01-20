from policyengine_us.model_api import *


class ia_fip_gross_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Iowa FIP gross earned income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.IA
    reference = (
        "https://www.legis.iowa.gov/docs/iac/chapter/01-07-2026.441.41.pdf"
    )

    adds = "gov.states.ia.dhs.fip.income.sources.earned"
