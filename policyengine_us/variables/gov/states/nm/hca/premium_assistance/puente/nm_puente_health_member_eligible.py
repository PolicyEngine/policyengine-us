from policyengine_us.model_api import *


class nm_puente_health_member_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Member eligible for New Mexico Puente Health"
    definition_period = YEAR
    defined_for = StateCode.NM
    reference = (
        # Addendum 2, Section I.A(1)-(2): a lawfully present non-citizen
        # ineligible for the federal PTC under Section 71302 (PY2026).
        "https://api.realfile.rtsclients.com/PublicFiles/6c91aefc960e463485b3474662fd7fd2/3527710a-f9f6-4e8f-9cd7-d9ea1010b653/Addendum%202_%20MAP%20P%26P%20Puente%20Health.pdf#page=2",
        # FINAL PY2027 MAP manual, Eligibility for Puente Health Program items
        # 1-2: Sections 71301 and 71302 (PY2027). The manual's summary bullet
        # on p.2 prints "Section 73101"; its eligibility section and 8.401.2.11
        # NMAC name Sections 71301 and 71302, the sections of Public Law
        # 119-21 that limit the credit, so 73101 is a misprint.
        "https://api.realfile.rtsclients.com/PublicFiles/6c91aefc960e463485b3474662fd7fd2/b61d3073-c0e6-4426-bb40-4cfef26fdca4/FINAL%202027%20MAP%20Policy%20and%20Procedures%20Manual.pdf#page=7",
        # 8.401.2.7(I) and 8.401.2.11(C)(2) NMAC. The rule in force is one
        # HTML page; HCA's proposed amendment reprints them on PDF pages 1 and
        # 5.
        "https://prod-rf-lambda.rtssaas.com/PublicFiles/d89c47bd0d70402dba89b03a22bda6d1/45b8668e-460f-45cd-804f-92ee3d442343/8.401.2.html",
        # PDF pages 1, 5
        "https://api.realfile.rtsclients.com/PublicFiles/6c91aefc960e463485b3474662fd7fd2/d3ee1d62-6f0f-4df7-b7fc-96a4c523ea89/08.401.0002_amended.pdf#page=1",
        # The repealed below-poverty rule for lawfully present immigrants.
        "https://www.law.cornell.edu/uscode/text/26/36B#c_1_B",
    )
    documentation = (
        "A Puente Health member is a lawfully present non-citizen 'who has "
        "become ineligible for the federal Premium Tax Credit due to the "
        "enactment of Section 71301 and 71302 of Public Law 119-21' "
        "(8.401.2.11(C) NMAC). The model finds these people with the same "
        "inputs the federal credit uses for those two sections, so the "
        "group is exactly the people the model's federal credit excludes "
        "under them. Section 71301 (from 2027): a status that "
        "gov.aca.ineligible_immigration_statuses bars from the credit, among "
        "the statuses that can buy a qualified health plan (DACA and "
        "undocumented status cannot; see the ineligible_immigration_statuses "
        "parameter). Section 71302 (from 2026): the people the repealed 26 "
        "U.S.C. 36B(c)(1)(B) treated as applicable taxpayers, read as "
        "aca_ptc_below_fpl_immigration_exception reads them: household "
        "income under the poverty line, a status the credit allows, and "
        "Medicaid-ineligible because of that status. The member must "
        "otherwise have qualified for the credit: in the tax family, not "
        "married filing separately, and without the other coverage that "
        "bars the credit (gov.aca.ineligible_coverage, which includes "
        "Medicaid). Last, the member must not be eligible for the federal "
        "credit (is_aca_ptc_eligible): Puente Health replaces a credit the "
        "person lost, so a person the model counts as credit-eligible, for "
        "example because Marketplace enrollment is supplied through "
        "pays_aca_premium, is not a member. Reading 'due to the "
        "enactment' as 'but for' those sections is a modeling choice. The "
        "sources name no filing requirement, so none applies."
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nm.hca.premium_assistance.puente
        p_aca = parameters(period).gov.aca
        status = person("immigration_status", period)
        non_citizen = status != status.possible_values.CITIZEN
        # 8.401.2.7(I) NMAC: a lawfully present individual is a non-citizen
        # whose status allows buying a qualified health plan on the exchange.
        qhp_status = ~np.isin(status.decode_to_str(), p.ineligible_immigration_statuses)
        lawfully_present = non_citizen & qhp_status
        credit_status = person("is_aca_ptc_immigration_status_eligible", period)
        # Section 71301: lawfully present, but in a status the federal credit
        # no longer allows. Nobody qualifies this way before 2027: until then
        # the federal list holds only statuses that cannot buy a qualified
        # health plan.
        section_71301 = lawfully_present & ~credit_status
        # Section 71302: the group aca_ptc_below_fpl_immigration_exception
        # covers, once the exception is no longer in effect.
        exception_repealed = not p_aca.below_fpl_immigration_exception_in_effect
        below_fpl = person.tax_unit("nm_premium_assistance_fpl_ratio", period) < 1
        medicaid_barred = ~person("is_medicaid_immigration_status_eligible", period)
        section_71302 = (
            exception_repealed
            & below_fpl
            & lawfully_present
            & credit_status
            & medicaid_barred
        )
        # The credit's other conditions: membership in the tax family (26
        # U.S.C. 36B(c)(1)(D)), no separate return, and no other coverage
        # that bars it (the coverage test of is_aca_marketplace_enrollee).
        tax_family_member = person("is_aca_tax_family_member", period)
        filing_status = person.tax_unit("filing_status", period)
        not_separate = filing_status != filing_status.possible_values.SEPARATE
        no_other_coverage = add(person, period, p_aca.ineligible_coverage) == 0
        # 8.401.2.11(C)(2) NMAC: the member "has become ineligible for the
        # federal Premium Tax Credit". The paths above find that group from
        # the credit's inputs; this keeps out anyone the model still counts
        # as credit-eligible, such as when pays_aca_premium is supplied.
        federal_credit_eligible = person("is_aca_ptc_eligible", period)
        return (
            (section_71301 | section_71302)
            & tax_family_member
            & not_separate
            & no_other_coverage
            & ~federal_credit_eligible
        )
