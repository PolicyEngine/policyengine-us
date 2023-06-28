from policyengine_us.model_api import *


class ia_exemption_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Iowa exemption credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.iowa.gov/sites/default/files/2021-12/IA6251%2841131%29.pdf"
        "https://tax.iowa.gov/sites/default/files/2023-01/IA6251%2841131%29.pdf"
    )
    defined_for = StateCode.IA

    def formula(tax_unit, period, parameters):
        # count adult and dependent exemptions
        adult_count = tax_unit("num", period)
        filing_status = tax_unit("filing_status", period)
        hoh_status = filing_status.possible_values.HEAD_OF_HOUSEHOLD
        hoh_bonus = where(filing_status == hoh_status, 1, 0)
        dependent_count = tax_unit("tax_unit_dependents", period)
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
