from policyengine_us.model_api import *


class ga_agi_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    label = "Georgia retirement exclusion"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://apps.dor.ga.gov/FillableForms/PDFViewer/Index?form=2022GA500"
        "https://advance.lexis.com/documentpage/?pdmfid=1000516&crid=fb5db531-a80f-4790-bddb-eefc8327ef60&config=00JAA1MDBlYzczZi1lYjFlLTQxMTgtYWE3OS02YTgyOGM2NWJlMDYKAFBvZENhdGFsb2feed0oM9qoQOMCSJFX5qkd&pddocfullpath=%2Fshared%2Fdocument%2Fstatutes-legislation%2Furn%3AcontentItem%3A65D2-CDH3-CGX8-044N-00008-00&pdcontentcomponentid=234186&pdteaserkey=sr1&pditab=allpods&ecomp=8s65kkk&earg=sr1&prid=66f02b0a-c5ae-4162-9535-127751546807"
    )
    defined_for = StateCode.GA

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(period).gov.states.ga.tax.income.agi.exclusions
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values

        cap = p.cap
        retirement_income = person("ga_retirement_income", period)

        # check disability and age eligibility
        disabled = person("is_disabled", period)
        aged = person("age", period) >= p.age

        # head exclusion
        head = person("is_tax_unit_head", period)
        head_exclusion_eligible = where(
            head & (disabled | aged), retirement_income, 0
        )
        head_exclusion = min_(tax_unit.sum(head_exclusion_eligible), cap)

        # spouse exclusion
        spouse = person("is_tax_unit_spouse", period)
        spouse_exclusion_eligible = where(
            (filing_status == status.JOINT) & (spouse & (disabled | aged)), retirement_income, 0
        )

        spouse_exclusion = min_(tax_unit.sum(spouse_exclusion_eligible), cap)

        # total retirement exclusion
        total_retirement_exclusion = head_exclusion + spouse_exclusion

        # military retirement income exclusion
        military_age = person("age", period) < p.military.age
        military_income = person("military_retirement_pay", period)
        earned_income = person("earned_income", period)

        # head military exclusion
        head_base = where(head & military_age, p.military.amount, 0)
        head_additional = where(
            head & (earned_income > p.military.additional_threshold), p.military.additional_amount,0)
        
        # ? does additional also require the 62 years old????????????????
        head_military_exclusion = min_(
            tax_unit.sum(head_base + head_additional), military_income)  # ???

        # spouse military exclusion
        spouse_base = where(spouse & military_age, p.military.amount, 0)
        spouse_additional = where(
            spouse & (earned_income > p.military.additional_threshold), p.military.additional_amount,0)

        spouse_military_exclusion = min_(
            tax_unit.sum(spouse_base + spouse_additional), military_income)  # ???

        # total military exclusion
        total_military_exclusion = head_military_exclusion + spouse_military_exclusion
    
        # total deduction
        return total_retirement_exclusion + total_military_exclusion