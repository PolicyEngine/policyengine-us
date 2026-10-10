from policyengine_us.model_api import *


class va_aged_blind_exemption_person(Variable):
    value_type = float
    entity = Person
    label = "Virginia aged/blind exemption for each person"
    defined_for = StateCode.VA
    unit = USD
    definition_period = YEAR
    reference = "https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.va.tax.income.exemptions
        aged_person = person("is_irs_aged", period).astype(int)
        blind_person = person("is_blind", period).astype(int)
        aged_blind_count = aged_person + blind_person
        # Va. Code 58.1-322.03(2)(b) grants the exemption to "each blind or
        # aged taxpayer" (the head or spouse), not to dependents, and has no
        # bar for a taxpayer whom another taxpayer can claim.
        filer = person("is_tax_unit_head_or_spouse", period)
        # A filer who forgoes this exemption to claim the low-income credit or
        # EITC gets none (Va. Code 58.1-339.8(D)(4)).
        claimed = person.tax_unit("va_claims_eitc_disqualifying_benefits", period)
        return claimed * filer * aged_blind_count * p.aged_blind
