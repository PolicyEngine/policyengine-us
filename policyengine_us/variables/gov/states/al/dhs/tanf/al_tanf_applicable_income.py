from policyengine_us.model_api import *


class al_tanf_applicable_income(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Applicable income for the Alabama family assistance (TANF)"
    defined_for = StateCode.AL
    definition_period = YEAR
    reference = "https://dhr.alabama.gov/wp-content/uploads/2023/10/DHR-FAD-595-Oct.23.pdf"

    adds = "gov.states.al.dhs.tanf.income_sources"
