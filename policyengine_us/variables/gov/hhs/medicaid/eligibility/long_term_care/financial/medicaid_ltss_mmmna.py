from policyengine_us.model_api import *


class medicaid_ltss_mmmna(Variable):
    value_type = float
    entity = Person
    label = "Medicaid LTSS minimum monthly maintenance needs allowance"
    unit = USD
    definition_period = MONTH
    default_value = 0
    documentation = (
        "Calculates the community spouse minimum monthly maintenance needs "
        "allowance standard for the modeled states. Texas pays the federal "
        "maximum as a flat spousal allowance (TX Appendix XXXI; MEPD "
        "J-7200). Delaware uses the federal minimum and shelter threshold, "
        "while Washington uses its published state standards under WAC "
        "182-513-1385(2). The allowance adds allowable community-spouse "
        "shelter expenses above the shelter threshold to the minimum in "
        "effect for the month (adjusted each July 1), capped at the federal "
        "maximum (adjusted each January 1) (DSSM 20910.4 "
        "through 20910.6; WAC 182-513-1385(3)(a) and (4)). It is a "
        "post-eligibility spousal protection standard, not an applicant "
        "income-eligibility deduction, so no eligibility screen reads it; "
        "the WAC 182-513-1385(3)(b) offset for the community spouse's own "
        "income belongs to the allocation, which is unmodeled. Texas "
        "Appendix XXXI labels this $4,066.50 figure the minimum monthly "
        "maintenance needs allowance, but it equals the federal maximum. "
        "Washington's published minimum and shelter threshold are $2,644 "
        "and $794 through June 2026, then $2,705 and $812 from July 2026. "
        "These published standards are used even where they differ from "
        "the unrounded federal arithmetic: January 2026 shelter expenses "
        "of $1,000 produce $2,850, rather than $2,850.625."
    )
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1396r-5#d",
        "https://www.medicaid.gov/federal-policy-guidance/downloads/cib05282025.pdf#page=2",
        "https://www.medicaid.gov/sites/default/files/2026-04/cib04272026.pdf#page=2",
        "https://fhb.hhs.texas.gov/sites/default/files/documents/mepd-26-2.pdf#page=465",
        "https://fhb.hhs.texas.gov/handbooks/medicaid-elderly-people-disabilities-handbook/j-7200-spousal-co-payment",
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=69",
        "https://app.leg.wa.gov/wac/default.aspx?cite=182-513-1385",
        "https://www.hca.wa.gov/assets/free-or-low-cost/income-standards-20260101.pdf#page=3",
        "https://www.hca.wa.gov/assets/free-or-low-cost/income-standards-20260701.pdf#page=3",
    )

    def formula_2026_01_01(person, period, parameters):
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

        minimum = where(
            state == states.WA,
            p.wa.mmmna.minimum,
            p.federal.mmmna.minimum,
        )
        shelter_threshold = where(
            state == states.WA,
            p.wa.mmmna.shelter_threshold,
            p.federal.mmmna.minimum * p.federal.mmmna.shelter_threshold_rate,
        )
        excess_shelter_expenses = max_(shelter_expenses - shelter_threshold, 0)
        formula_mmmna = min_(
            minimum + excess_shelter_expenses,
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
