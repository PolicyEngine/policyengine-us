from policyengine_us.model_api import *


class nm_aged_blind_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico aged and blind exemption"
    unit = USD
    definition_period = YEAR
    reference = (
        # 7-2-5.2. EXEMPTION--INCOME OF PERSONS SIXTY-FIVE AND OLDER OR BLIND Page 22
        "https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/34821a9573ca43e7b06dfad20f5183fd/856ebf4b-3814-49dd-8631-ebe579d6a42b/Personal%20Income%20Tax.pdf#page=34",
        # Tax Form Instructions Page ADJ-5 TABLE 1. Exemptions for Persons 65 or Older or Blind
        "https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/34821a9573ca43e7b06dfad20f5183fd/1afc56af-ea90-4d48-82e5-1f9aeb43255a/PITbook2022.pdf#page=50",
        # 7-2-5.2. Exemption; income of persons sixty-five and older or blind
        "https://nmonesource.com/nmos/nmsa/en/item/4340/index.do#!fragment/zoupio-_Toc140503666/BQCwhgziBcwMYgK4DsDWszIQewE4BUBTADwBdoAvbRABwEtsBaAfX2zgEYAWABgFYeAZgBsogJQAaZNlKEIARUSFcAT2gBydRIiEwuBIuVrN23fpABlPKQBCagEoBRADKOAagEEAcgGFHE0jAAI2hSdjExIA",
    )
    defined_for = StateCode.NM

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.nm.tax.income.exemptions.blind_and_aged
        filing_status = tax_unit("filing_status", period)
        statuses = filing_status.possible_values
        agi = tax_unit("adjusted_gross_income", period)
        age_threshold = p.age_threshold

        # Check if taxpayer is blind or aged.
        blind_head = tax_unit("blind_head", period)
        aged_head = tax_unit("age_head", period) >= age_threshold

        # Check if taxpayer is eligible.
        # New Mexico does not double exemptions if the same individual is both aged and blind.
        head_eligible = blind_head | aged_head

        # Check if spouse is blind or aged.
        blind_spouse = tax_unit("blind_spouse", period)
        aged_spouse = tax_unit("age_spouse", period) >= age_threshold

        # Check if spouse is eligible.
        spouse_eligible = blind_spouse | aged_spouse

        eligible_count = head_eligible.astype(int) + spouse_eligible.astype(
            int
        )

        # Use `right=True` to reflect "over ... but not over ...".
        amount = select(
            [
                filing_status == statuses.SINGLE,
                filing_status == statuses.JOINT,
                filing_status == statuses.HEAD_OF_HOUSEHOLD,
                filing_status == statuses.SEPARATE,
                filing_status == statuses.SURVIVING_SPOUSE,
            ],
            [
                p.single.calc(agi, right=True),
                p.joint.calc(agi, right=True),
                p.head_of_household.calc(agi, right=True),
                p.separate.calc(agi, right=True),
                p.widow.calc(agi, right=True),
            ],
        )
        return eligible_count * amount
