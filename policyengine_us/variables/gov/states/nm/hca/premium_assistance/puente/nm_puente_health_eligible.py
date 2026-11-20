from policyengine_us.model_api import *


class nm_puente_health_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for New Mexico Puente Health"
    definition_period = YEAR
    defined_for = StateCode.NM
    reference = (
        # Addendum 2, Section I.A: eligibility for PY2026.
        "https://api.realfile.rtsclients.com/PublicFiles/6c91aefc960e463485b3474662fd7fd2/3527710a-f9f6-4e8f-9cd7-d9ea1010b653/Addendum%202_%20MAP%20P%26P%20Puente%20Health.pdf#page=2",
        # FINAL PY2027 MAP manual, Eligibility for Puente Health Program.
        "https://api.realfile.rtsclients.com/PublicFiles/6c91aefc960e463485b3474662fd7fd2/b61d3073-c0e6-4426-bb40-4cfef26fdca4/FINAL%202027%20MAP%20Policy%20and%20Procedures%20Manual.pdf#page=7",
        # 8.401.2.7(G) and 8.401.2.11(C) NMAC. The rule in force is one HTML
        # page; HCA's proposed amendment reprints them on PDF pages 1 and 5.
        "https://prod-rf-lambda.rtssaas.com/PublicFiles/d89c47bd0d70402dba89b03a22bda6d1/45b8668e-460f-45cd-804f-92ee3d442343/8.401.2.html",
        # PDF pages 1, 5
        "https://api.realfile.rtsclients.com/PublicFiles/6c91aefc960e463485b3474662fd7fd2/d3ee1d62-6f0f-4df7-b7fc-96a4c523ea89/08.401.0002_amended.pdf#page=1",
    )
    documentation = (
        "A tax unit qualifies for Puente Health when the program is in "
        "effect, at least one member is a Puente Health member "
        "(nm_puente_health_member_eligible: a lawfully present non-citizen "
        "who lost the federal premium tax credit under Public Law 119-21 "
        "Section 71301 or 71302), and household income is at or below the "
        "income limit: 100% of the poverty line in PY2026 (Addendum 2) and "
        "400% in PY2027 (FINAL PY2027 MAP manual), on "
        "nm_premium_assistance_fpl_ratio, the exact ratio of ACA MAGI to "
        "aca_fpg. The sources impose no tax filing or reconciliation "
        "requirement, so none is applied."
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nm.hca.premium_assistance.puente
        has_member = add(tax_unit, period, ["nm_puente_health_member_eligible"]) > 0
        ratio = tax_unit("nm_premium_assistance_fpl_ratio", period)
        income_eligible = ratio <= p.fpl_limit
        return p.in_effect & has_member & income_eligible
