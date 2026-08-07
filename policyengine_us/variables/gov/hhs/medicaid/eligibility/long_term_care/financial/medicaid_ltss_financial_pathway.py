from policyengine_us.model_api import *


class MedicaidLTSSFinancialPathway(Enum):
    UNMODELED = "Unmodeled"
    SPECIAL_INCOME = "Special income"
    INSTITUTIONAL_MEDICALLY_NEEDY = "Institutional medically needy"


class medicaid_ltss_financial_pathway(Variable):
    value_type = Enum
    possible_values = MedicaidLTSSFinancialPathway
    default_value = MedicaidLTSSFinancialPathway.UNMODELED
    entity = Person
    label = "Medicaid LTSS financial pathway"
    definition_period = MONTH
    documentation = (
        "Identifies the modeled financial pathway for the opt-in Medicaid "
        "long-term services and supports threshold screen. Institutional "
        "pathways are modeled for Texas, Delaware, and Washington. HCBS "
        "pathways are modeled only for Washington's source-named COPES, New "
        "Freedom, and Residential Support waivers. All other states, settings, "
        "waivers, and unsupported assistance-unit sizes are unmodeled."
    )
    reference = (
        "https://fhb.hhs.texas.gov/handbooks/medicaid-elderly-people-disabilities-handbook/appendix-xxxi-budget-reference-chart",
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/13aee487-1cd1-4726-addf-63603af28a78",
        "https://app.leg.wa.gov/wac/default.aspx?cite=182-513-1395",
        "https://www.hca.wa.gov/free-or-low-cost-health-care/i-help-others-apply-and-access-apple-health/wac-182-515-1505-home-and-community-based-hcb-waiver-services-authorized-home-and-community-services-hcs",
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

        institutional = (setting == settings.INSTITUTIONAL) & (waiver == waivers.NONE)
        washington_hcbs = (setting == settings.HCBS) & (
            ((waiver == waivers.WA_COPES) & p.wa.waivers.copes.enabled)
            | ((waiver == waivers.WA_NEW_FREEDOM) & p.wa.waivers.new_freedom.enabled)
            | ((waiver == waivers.WA_RSW) & p.wa.waivers.rsw.enabled)
        )

        texas_or_delaware_institutional = (
            institutional
            & ((state == states.TX) | (state == states.DE))
            & ((assistance_unit_size == 1) | (assistance_unit_size == 2))
        )
        washington_modeled_setting = (
            (state == states.WA)
            & (institutional | washington_hcbs)
            & (assistance_unit_size == 1)
        )
        washington_special_income = washington_modeled_setting & (
            income <= p.wa.special_income_limit.individual
        )
        washington_medically_needy = washington_modeled_setting & (
            income > p.wa.special_income_limit.individual
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
