from policyengine_us.model_api import *


class nm_property_tax_rebate_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the New Mexico property tax rebate"
    definition_period = YEAR
    reference = "https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/34821a9573ca43e7b06dfad20f5183fd/1afc56af-ea90-4d48-82e5-1f9aeb43255a/PITbook2022.pdf"
    defined_for = StateCode.NM

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nm.tax.income.rebates.property_tax
        # Head or spouse eligible if 65 or over.
        age_head = tax_unit("age_head", period)
        age_spouse = tax_unit("age_spouse", period)
        head_age_eligible = age_head >= p.age_eligibility
        spouse_age_eligible = age_spouse >= p.age_eligibility
        age_eligible = head_age_eligible | spouse_age_eligible
        # Person eligible if income at or below $16,000
        agi = tax_unit("nm_agi", period)
        agi_eligible = agi <= p.income_threshold
        return age_eligible & agi_eligible
