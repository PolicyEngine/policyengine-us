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
        # 422.5(3)(a) before the 2023 renumbering.
        "https://www.legis.iowa.gov/docs/code/2022/422.5.pdf#page=3",
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
        # Iowa Code 422.5 denies the exemption to a claimed dependent only
        # when the person claiming them has net income over the limit. The
        # instructions instead test the dependent's own income against
        # $5,000 and limit the exemption to filers not claimed on another
        # Iowa return; the statute governs.
        disqualified = tax_unit("ia_claimed_filer_income_disqualified", period)
        return exempt & ~disqualified
