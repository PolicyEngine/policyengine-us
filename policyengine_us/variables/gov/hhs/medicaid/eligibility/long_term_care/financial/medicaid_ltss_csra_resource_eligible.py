from policyengine_us.model_api import *


class medicaid_ltss_csra_resource_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Meets modeled Medicaid LTSS resource threshold after CSRA"
    definition_period = MONTH
    documentation = (
        "Tests trusted comprehensive LTSS countable-resource inputs. For an "
        "applicant with a community spouse, the initial CSRA is the greater "
        "of the applicable state/federal floor or the fixed statutory "
        "one-half of the couple's snapshot resources under 42 USC "
        "1396r-5(f)(2)(A), capped at the federal maximum. Delaware's "
        "$25,000 state spousal share (DSSM 20910.10) sits below the federal "
        "minimum, which therefore governs. Court and fair-hearing "
        "adjustments, resource-hardship overrides, and detailed state asset "
        "exclusions are not modeled."
    )
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1396r-5#f_2",
        "https://fhb.hhs.texas.gov/handbooks/medicaid-elderly-people-disabilities-handbook/appendix-xxxi-budget-reference-chart",
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/13aee487-1cd1-4726-addf-63603af28a78",
        "https://www.hca.wa.gov/assets/free-or-low-cost/income-standards-20260101.pdf#page=3",
    )

    def formula_2026_01_01(person, period, parameters):
        p = parameters(period).gov.hhs.medicaid.eligibility.long_term_care.financial
        state = person.household("state_code", period)
        states = state.possible_values
        pathway = person("medicaid_ltss_financial_pathway", period)
        pathways = pathway.possible_values
        assistance_unit_size = person("medicaid_ltss_assistance_unit_size", period)
        resources = person("medicaid_ltss_countable_resources", period)

        resource_limit = select(
            [
                (state == states.TX) & (assistance_unit_size == 1),
                (state == states.TX) & (assistance_unit_size == 2),
                (state == states.DE) & (assistance_unit_size == 1),
                (state == states.DE) & (assistance_unit_size == 2),
                (state == states.WA) & (assistance_unit_size == 1),
            ],
            [
                p.tx.resources.individual,
                p.tx.resources.couple,
                p.de.resources.individual,
                p.de.resources.couple,
                p.wa.resources.individual,
            ],
            default=0,
        )
        no_community_spouse_eligible = resources <= resource_limit

        state_csra_minimum = select(
            [
                state == states.TX,
                state == states.DE,
                state == states.WA,
            ],
            [
                max_(p.tx.csra.state_minimum, p.federal.csra.minimum),
                max_(p.de.csra.state_minimum, p.federal.csra.minimum),
                max_(p.wa.csra.state_minimum, p.federal.csra.minimum),
            ],
            default=0,
        )
        snapshot_resources = person(
            "medicaid_ltss_couple_countable_resources_at_first_institutionalization",
            period,
        )
        csra = min_(
            max_(snapshot_resources / 2, state_csra_minimum),
            p.federal.csra.maximum,
        )
        current_couple_resources = resources + person(
            "medicaid_ltss_community_spouse_countable_resources",
            period,
        )
        has_community_spouse = person("medicaid_ltss_has_community_spouse", period)
        community_spouse_eligible = (assistance_unit_size == 1) & (
            current_couple_resources <= csra + resource_limit
        )
        modeled_pathway = pathway != pathways.UNMODELED

        return modeled_pathway & where(
            has_community_spouse,
            community_spouse_eligible,
            no_community_spouse_eligible,
        )
