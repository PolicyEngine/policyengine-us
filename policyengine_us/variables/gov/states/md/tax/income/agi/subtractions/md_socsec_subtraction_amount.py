from policyengine_us.model_api import *


class md_socsec_subtraction_amount(Variable):
    value_type = float
    entity = Person
    label = "MD social security subtraction from AGI"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://casetext.com/statute/code-of-maryland/article-tax-general/title-10-income-tax/subtitle-2-maryland-taxable-income-calculations-for-individual/part-ii-maryland-adjusted-gross-income/section-10-208-effective-until-712024-subtractions-from-federal-adjusted-gross-income-state-adjustments"
        "https://www.marylandtaxes.gov/forms/21_forms/Resident_Booklet.pdf#page=14"
    )
    defined_for = StateCode.MD
    adds = ["taxable_social_security"]
