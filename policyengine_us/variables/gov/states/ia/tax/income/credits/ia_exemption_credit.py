from policyengine_us.model_api import *


class ia_exemption_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Iowa exemption credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenue.iowa.gov/sites/default/files/2021-12/IA6251%2841131%29.pdf",
        "https://revenue.iowa.gov/sites/default/files/2023-01/IA6251%2841131%29.pdf",
        "https://www.legis.iowa.gov/docs/code/2026/422.pdf#page=39",
        # 2025 IA 1040 instructions, Personal and dependent credits.
        "https://revenue.iowa.gov/media/4435/download?inline#page=8",
    )
    defined_for = StateCode.IA

    def formula(tax_unit, period, parameters):
        # count adult and dependent exemptions
        adult_count = tax_unit("head_spouse_count", period)
        filing_status = tax_unit("filing_status", period)
        hoh_status = filing_status.possible_values.HEAD_OF_HOUSEHOLD
        hoh_bonus = filing_status == hoh_status
        # Iowa Code 422.12(1)(a) gives "dependent" its Internal Revenue Code
        # meaning, and the instructions count the dependents "you are
        # claiming for federal income tax purposes". Under IRC 152(b)(1) a
        # return on which the filer (or, if joint, either spouse) can be
        # claimed has none. Each filer keeps the personal credit, which
        # Iowa allows "even if you are claimed as a dependent".
        filer_is_dependent = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
        dependent_count = where(
            filer_is_dependent, 0, tax_unit("tax_unit_dependents", period)
        )
        # count extra adult exemptions based on being elderly and/or blind
        p = parameters(period).gov.states.ia.tax.income
        exemption = p.credits.exemption
        elder_head = tax_unit("age_head", period) >= exemption.elderly_age
        elder_spouse = tax_unit("age_spouse", period) >= exemption.elderly_age
        elder_count = elder_head.astype(int) + elder_spouse.astype(int)
        blind_head = tax_unit("blind_head", period)
        blind_spouse = tax_unit("blind_spouse", period)
        blind_count = blind_head.astype(int) + blind_spouse.astype(int)
        additional_count = elder_count + blind_count
        return (
            (adult_count + hoh_bonus) * exemption.personal
            + additional_count * exemption.additional
            + dependent_count * exemption.dependent
        )
