from policyengine_us.model_api import *


class medicaid_ltss_mmmna(Variable):
    value_type = float
    entity = Person
    label = "Medicaid LTSS minimum monthly maintenance needs allowance"
    unit = USD
    definition_period = MONTH
    documentation = (
        "Calculates the community spouse minimum monthly maintenance needs "
        "allowance standard for the modeled states. Texas pays the federal "
        "maximum as a flat spousal allowance (TX Appendix XXXI; MEPD "
        "J-7200). Delaware and Washington use the federal formula: the July "
        "2026 minimum plus allowable community-spouse shelter expenses "
        "above the excess-shelter threshold, supplied as an explicit input, "
        "capped at the federal maximum (DSSM 20910.4 through 20910.6; WAC "
        "182-513-1385(3)(a) and (4)). It is a post-eligibility spousal "
        "protection standard, not an applicant income-eligibility "
        "deduction; the WAC 182-513-1385(3)(b) offset for the community "
        "spouse's own income belongs to the allocation, which is unmodeled. "
        "The whole variable is unmodeled before July 2026, when the "
        "effective-dated federal minimum begins; this also defers the Texas "
        "flat maximum, which is otherwise effective January 1, 2026."
    )
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1396r-5#d",
        "https://www.medicaid.gov/sites/default/files/2026-04/cib04272026.pdf#page=2",
        "https://fhb.hhs.texas.gov/handbooks/medicaid-elderly-people-disabilities-handbook/appendix-xxxi-budget-reference-chart",
        "https://fhb.hhs.texas.gov/handbooks/medicaid-elderly-people-disabilities-handbook/j-7200-spousal-co-payment",
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/13aee487-1cd1-4726-addf-63603af28a78",
        "https://app.leg.wa.gov/wac/default.aspx?cite=182-513-1385",
    )

    def formula_2026_07_01(person, period, parameters):
        p = parameters(period).gov.hhs.medicaid.eligibility.long_term_care.financial
        state = person.household("state_code", period)
        states = state.possible_values
        pathway = person("medicaid_ltss_financial_pathway", period)
        pathways = pathway.possible_values
        has_community_spouse = person("medicaid_ltss_has_community_spouse", period)
        shelter_expenses = person(
            "medicaid_ltss_community_spouse_shelter_expenses",
            period,
        )

        excess_shelter_expenses = max_(
            shelter_expenses
            - (p.federal.mmmna.minimum * p.federal.mmmna.shelter_threshold_rate),
            0,
        )
        formula_mmmna = min_(
            p.federal.mmmna.minimum + excess_shelter_expenses,
            p.federal.mmmna.maximum,
        )
        mmmna = where(
            state == states.TX,
            p.federal.mmmna.maximum,
            formula_mmmna,
        )
        return where(
            (pathway != pathways.UNMODELED) & has_community_spouse,
            mmmna,
            0,
        )
