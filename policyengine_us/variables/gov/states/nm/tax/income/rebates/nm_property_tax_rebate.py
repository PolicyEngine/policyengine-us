from policyengine_us.model_api import *


class nm_property_tax_rebate(Variable):
    value_type = float
    entity = Person
    label = "New Mexico property tax rebate"
    unit = USD
    definition_period = YEAR
    reference = "https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/34821a9573ca43e7b06dfad20f5183fd/1afc56af-ea90-4d48-82e5-1f9aeb43255a/PITbook2022.pdf"
    defined_for = StateCode.NM

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nm.tax.income.rebates.property_tax
        # Person eligible if 65 or over
        age = person("age", period)
        age_eligible = age >= p.age_eligibility
        # Person eligible if income below $16,000
        agi = person.tax_unit("nm_agi", period)
        agi_eligible = agi <= p.income_threshold
        eligible = age_eligible & agi_eligible
        # Get property tax paid by person
        ptax_owner = person("real_estate_taxes", period)
        # Get person rent and multiply by 6%
        rent = person("rent", period)
        rent_percent = rent * p.rate
        rent_and_ptax = ptax_owner + rent_percent
        # Get the maximum tax liability
        max_liability = p.max_liability.calc(agi)
        rebate = max_(0, rent_and_ptax - max_liability)
        # Cap is based on filing status
        filing_status = person.tax_unit("filing_status", period)
        return eligible * min_(rebate, p.cap[filing_status])
