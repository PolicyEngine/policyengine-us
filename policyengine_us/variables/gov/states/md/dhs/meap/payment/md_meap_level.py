from policyengine_us.model_api import *


class md_meap_level(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Maryland MEAP heating payment level"
    defined_for = StateCode.MD
    reference = (
        "https://dhs.maryland.gov/documents/OHEP/Advisory%20Board/FY26-MEAP-Benefit-Matrix-2-1-1.pdf",
        "https://dhs.maryland.gov/documents/OHEP/OHEP-Operations-Manual.pdf#page=62,63",
    )
    documentation = "Submetered and subsidized homes use Level 6. The over-200% categorical nominal level takes precedence over these housing categories; this precedence follows the manual's nominal-payment instruction. Existing assistance inputs approximate the regulation's narrower subsidy definition."

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.md.dhs.meap.payment
        ratio = spm_unit("md_meap_countable_income", period) / spm_unit(
            "md_meap_fpg", period
        )
        # Inclusive band tops resolve the gaps between integer percentage labels.
        income_level = p.income_level.calc(ratio, right=True)
        subsidized = spm_unit(
            "receives_housing_assistance", period
        ) | spm_unit.household("is_in_public_housing", period)
        dwelling = spm_unit("md_meap_dwelling_type", period)
        submetered = dwelling == dwelling.possible_values.SUB_METERED
        return where(
            (income_level != p.nominal_level) & (subsidized | submetered),
            p.subsidized_level,
            income_level,
        )
