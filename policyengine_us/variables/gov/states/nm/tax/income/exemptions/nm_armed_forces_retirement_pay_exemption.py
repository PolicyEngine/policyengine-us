from policyengine_us.model_api import *


class nm_armed_forces_retirement_pay_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico armed forces retirement pay exemption"
    unit = USD
    definition_period = YEAR
    reference = "https://casetext.com/statute/new-mexico-statutes-1978/chapter-7-taxation/article-2-income-tax-general-provisions/section-7-2-513-effective-until-112025-exemption-armed-forces-retirement-pay"
    defined_for = StateCode.NM

    adds = ["nm_armed_forces_retirement_pay_exemption_person"]
