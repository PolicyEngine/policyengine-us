from policyengine_us.model_api import *


class ga_retirement_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    label = "Georgia retirement exclusion"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.georgia.gov/document/booklet/2021-it-511-individual-income-tax-booklet/download"
        "https://dor.georgia.gov/document/document/2022-it-511-individual-income-tax-booklet/download"
        "https://advance.lexis.com/documentpage/?pdmfid=1000516&crid=fb5db531-a80f-4790-bddb-eefc8327ef60&config=00JAA1MDBlYzczZi1lYjFlLTQxMTgtYWE3OS02YTgyOGM2NWJlMDYKAFBvZENhdGFsb2feed0oM9qoQOMCSJFX5qkd&pddocfullpath=%2Fshared%2Fdocument%2Fstatutes-legislation%2Furn%3AcontentItem%3A65D2-CDH3-CGX8-044N-00008-00&pdcontentcomponentid=234186&pdteaserkey=sr1&pditab=allpods&ecomp=8s65kkk&earg=sr1&prid=66f02b0a-c5ae-4162-9535-127751546807"
    )
    defined_for = StateCode.GA

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(period).gov.states.ga.tax.income.agi.exclusions
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values
        earned_income_exclusion_eligible = person(
            "ga_earned_income_exclusion", period
        )
        retirement_income_eligible = (
            person("ga_retirement_income", period)
            + earned_income_exclusion_eligible
        )
        # All retirement income that eligible for retirement exclusion except military retirement income

        ## check disability, age eligibility and caps
        disabled = person("is_disabled", period)
        age_younger = (person("age", period) >= p.retirement.age.younger) & (
            person("age", period) < p.retirement.age.older
        )
        age_older = person("age", period) >= p.retirement.age.older
        cap_younger_age = p.retirement.cap.exclusion_younger_age
        cap_older_age = p.retirement.cap.exclusion_older_age
        exclusion_eligible_younger = min_(
            retirement_income_eligible, cap_younger_age
        )
        exclusion_eligible_older = min_(
            retirement_income_eligible, cap_older_age
        )

        ## head exclusion
        head = person("is_tax_unit_head", period)
        head_older_exclusion = where(
            (head & age_older), exclusion_eligible_older, 0
        )
        head_exclusion = tax_unit.sum(
            where(
                head & (disabled | age_younger),
                exclusion_eligible_younger,
                head_older_exclusion,
            )
        )

        ## spouse exclusion
        spouse = person("is_tax_unit_spouse", period)
        spouse_older_exclusion = where(
            (filing_status == status.JOINT) & (spouse & age_older),
            exclusion_eligible_older,
            0,
        )

        spouse_exclusion = tax_unit.sum(
            where(
                (filing_status == status.JOINT)
                & spouse
                & (disabled | age_younger),
                exclusion_eligible_younger,
                spouse_older_exclusion,
            )
        )

        ## military exclusion
        military_exclusion = tax_unit(
            "ga_military_retirement_exclusion", period
        )

        # total retirement exclusions
        return head_exclusion + spouse_exclusion + military_exclusion
