from policyengine_us.model_api import *


class ia_claimed_filer_income_disqualified(Variable):
    value_type = bool
    entity = TaxUnit
    label = (
        "Iowa low-income relief denied because a claiming person's income is too high"
    )
    documentation = (
        "Iowa Code 422.5 denies the benefit of its low-income subsection "
        "(the exemption, the single-filer tax reduction and the alternate "
        "tax) to a person claimed as a dependent on another return when the "
        "person claiming them has net income over the subsection's limit. "
        "The test reads an actual claim, not claimability, and the claiming "
        "person's income, not the dependent filer's."
    )
    definition_period = YEAR
    defined_for = StateCode.IA
    reference = (
        # 2021-2022: 422.5(3)(a) and (3B); renumbered (2) and (3) from 2023.
        "https://www.legis.iowa.gov/docs/code/2022/422.5.pdf#page=3",
        # PDF pages 1-2
        "https://www.legis.iowa.gov/docs/code/2024/422.5.pdf#page=1",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ia.tax.income.tax_exempt
        # The active subsection is the elderly one when either filer of this
        # return is 65 or older.
        elderly = (tax_unit("age_head", period) >= p.elderly_age) | (
            tax_unit("age_spouse", period) >= p.elderly_age
        )
        smaller_limit = where(
            elderly, p.income_limit.single_elderly, p.income_limit.single_nonelderly
        )
        larger_limit = where(
            elderly, p.income_limit.other_elderly, p.income_limit.other_nonelderly
        )
        person = tax_unit.members
        filer = person("is_tax_unit_head_or_spouse", period)
        claimed = person("claimed_as_dependent_on_another_return", period)
        claimant_status = person("ia_dependent_claimant_filing_status", period)
        statuses = claimant_status.possible_values
        larger_status = (
            (claimant_status == statuses.JOINT)
            | (claimant_status == statuses.HEAD_OF_HOUSEHOLD)
            | (claimant_status == statuses.SURVIVING_SPOUSE)
        )
        married = (claimant_status == statuses.JOINT) | (
            claimant_status == statuses.SEPARATE
        )
        claimant_limit = where(
            larger_status,
            person.tax_unit.project(larger_limit),
            person.tax_unit.project(smaller_limit),
        )
        claimant_income = person("ia_dependent_claimant_net_income", period)
        combined_income = claimant_income + person(
            "ia_dependent_claimant_spouse_net_income", period
        )
        # The statute denies relief only when income "exceeds" the limit.
        over_limit = (claimant_income > claimant_limit) | (
            married & (combined_income > person.tax_unit.project(larger_limit))
        )
        return tax_unit.any(filer & claimed & over_limit)
