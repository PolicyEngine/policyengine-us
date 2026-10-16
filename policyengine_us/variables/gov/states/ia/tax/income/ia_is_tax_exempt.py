from policyengine_us.model_api import *


class ia_is_tax_exempt(Variable):
    value_type = bool
    entity = TaxUnit
    label = "whether or not exempt from Iowa income tax because of low income"
    definition_period = YEAR
    reference = (
        "https://revenue.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdf",
        "https://revenue.iowa.gov/media/2650/download?inline#page=38",
        "https://revenue.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdf",
        "https://revenue.iowa.gov/media/2721/download?inline#page=37",
        "https://revenue.iowa.gov/media/2811/download?inline#page=12",
        "https://revenue.iowa.gov/media/4152/download?inline#page=10",
        "https://revenue.iowa.gov/media/4435/download?inline#page=11",
        # PDF pages 7-8: Iowa Code 422.5(2)(a) and (3)(a).
        "https://www.legis.iowa.gov/docs/code/2026/422.pdf#page=7",
    )
    defined_for = StateCode.IA

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        is_single = filing_status == filing_status.possible_values.SINGLE
        p = parameters(period).gov.states.ia.tax.income.tax_exempt
        elderly_head = tax_unit("age_head", period) >= p.elderly_age
        elderly_spouse = tax_unit("age_spouse", period) >= p.elderly_age
        is_elderly = elderly_head | elderly_spouse
        pil = p.income_limit
        modified_income_limit = where(
            is_single,
            where(is_elderly, pil.single_elderly, pil.single_nonelderly),
            where(is_elderly, pil.other_elderly, pil.other_nonelderly),
        )
        exempt = tax_unit("ia_modified_income", period) <= modified_income_limit
        # The instructions limit the ordinary exemption to filers who are "not
        # claimed as a dependent on another person's Iowa return". A single
        # filer who is claimed is instead exempt when income, without adding
        # back deductions, is "less than $5,000"; every non-single status
        # (joint, head of household, surviving spouse or married filing
        # separately) is not exempt if any filer is claimed.
        # Iowa Code 422.5(2)-(3) denies the exemption only when the
        # claimer's own net income exceeds the limit; the model has no input
        # for the claimer's income, so it follows the instructions. Both turn
        # on being claimed, not on being claimable, so this reads the claim.
        person = tax_unit.members
        filer = person("is_tax_unit_head_or_spouse", period)
        claimed = person("claimed_as_dependent_on_another_return", period)
        filer_is_dependent = tax_unit.any(filer & claimed)
        dependent_income = add(tax_unit, period, p.dependent.income_sources)
        dependent_exempt = is_single & (dependent_income < p.dependent.income_limit)
        return where(filer_is_dependent, dependent_exempt, exempt)
