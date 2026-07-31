from policyengine_us.model_api import *


class medicaid_ltss_mmmna(Variable):
    value_type = float
    entity = Person
    label = "Medicaid LTSS minimum monthly maintenance needs allowance"
    unit = USD
    definition_period = MONTH
    documentation = (
        "Calculates the federal MMMNA standard from the July 2026 minimum, "
        "allowable community-spouse shelter expenses supplied as an explicit "
        "input, and the federal maximum. It is a post-eligibility spousal "
        "protection standard, not an applicant income-eligibility deduction. "
        "The January-through-June 2026 minimum is left unmodeled."
    )
    reference = (
        "https://www.medicaid.gov/sites/default/files/2026-04/cib04272026.pdf",
        "https://www.law.cornell.edu/uscode/text/42/1396r-5",
    )

    def formula_2026_07_01(person, period, parameters):
        p = parameters(period).gov.hhs.medicaid.eligibility.long_term_care.financial
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
        mmmna = min_(
            p.federal.mmmna.minimum + excess_shelter_expenses,
            p.federal.mmmna.maximum,
        )
        return where(
            (pathway != pathways.UNMODELED) & has_community_spouse,
            mmmna,
            0,
        )
