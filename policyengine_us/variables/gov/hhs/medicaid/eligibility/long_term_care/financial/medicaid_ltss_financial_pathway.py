from policyengine_us.model_api import *


class MedicaidLTSSFinancialPathway(Enum):
    SPECIAL_INCOME = "Special income"
    INSTITUTIONAL_MEDICALLY_NEEDY = "Institutional medically needy"
    UNMODELED = "Unmodeled"


class medicaid_ltss_financial_pathway(Variable):
    value_type = Enum
    possible_values = MedicaidLTSSFinancialPathway
    default_value = MedicaidLTSSFinancialPathway.UNMODELED
    entity = Person
    label = "Medicaid LTSS financial pathway"
    definition_period = MONTH
    documentation = (
        "Identifies the modeled financial pathway for the opt-in Medicaid "
        "long-term services and supports threshold screen. Every modeled "
        "route is SSI-related, so a person who is not aged, blind, or "
        "disabled is unmodeled (42 CFR 435.236; 42 CFR 435.1005). "
        "Institutional pathways are modeled for Texas, Delaware, and "
        "Washington. HCBS pathways are modeled only for Washington's "
        "source-named COPES, New Freedom, and Residential Support waivers; "
        "their enabled flags exist for reform analysis, so the disabled "
        "branch is reform-only-reachable. All other states, settings, "
        "waivers, and unsupported assistance-unit sizes are unmodeled. "
        "Aged, blind, or disabled status is an annual input, so it cannot "
        "change within a year on this monthly screen. The setting input is "
        "independent of is_in_medicaid_facility; populating only that "
        "variable leaves the setting UNKNOWN and the pathway unmodeled."
    )
    reference = (
        "https://www.law.cornell.edu/cfr/text/42/435.236",
        "https://www.law.cornell.edu/cfr/text/42/435.1005",
        "https://fhb.hhs.texas.gov/sites/default/files/documents/mepd-26-2.pdf#page=465",
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=1",
        "https://app.leg.wa.gov/wac/default.aspx?cite=182-513-1395",
        "https://app.leg.wa.gov/wac/default.aspx?cite=182-515-1505",
    )

    def formula_2026_01_01(person, period, parameters):
        p = parameters(period).gov.hhs.medicaid.eligibility.long_term_care.financial
        state = person.household("state_code", period)
        states = state.possible_values
        setting = person("medicaid_ltss_setting", period)
        settings = setting.possible_values
        waiver = person("medicaid_ltss_waiver", period)
        waivers = waiver.possible_values
        assistance_unit_size = person("medicaid_ltss_assistance_unit_size", period)
        income = person("medicaid_ltss_qit_adjusted_income", period)
        special_income_limit = person("medicaid_ltss_special_income_limit", period)
        aged_blind_disabled = person("is_ssi_aged_blind_disabled", period.this_year)

        institutional = (setting == settings.INSTITUTIONAL) & (waiver == waivers.NONE)
        washington_hcbs = (setting == settings.HCBS) & (
            ((waiver == waivers.WA_COPES) & p.wa.waivers.copes.enabled)
            | ((waiver == waivers.WA_NEW_FREEDOM) & p.wa.waivers.new_freedom.enabled)
            | ((waiver == waivers.WA_RSW) & p.wa.waivers.rsw.enabled)
        )

        texas_or_delaware_institutional = (
            institutional
            & aged_blind_disabled
            & ((state == states.TX) | (state == states.DE))
            & ((assistance_unit_size == 1) | (assistance_unit_size == 2))
        )
        washington_modeled_setting = (
            (state == states.WA)
            & aged_blind_disabled
            & (institutional | washington_hcbs)
            & (assistance_unit_size == 1)
        )
        washington_special_income = washington_modeled_setting & (
            income <= special_income_limit
        )
        washington_medically_needy = washington_modeled_setting & (
            income > special_income_limit
        )

        return select(
            [
                texas_or_delaware_institutional,
                washington_special_income,
                washington_medically_needy,
            ],
            [
                MedicaidLTSSFinancialPathway.SPECIAL_INCOME,
                MedicaidLTSSFinancialPathway.SPECIAL_INCOME,
                MedicaidLTSSFinancialPathway.INSTITUTIONAL_MEDICALLY_NEEDY,
            ],
            default=MedicaidLTSSFinancialPathway.UNMODELED,
        )
