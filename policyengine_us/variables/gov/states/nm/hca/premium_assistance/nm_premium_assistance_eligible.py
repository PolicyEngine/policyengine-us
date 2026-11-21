from policyengine_us.model_api import *


class nm_premium_assistance_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for base New Mexico Premium Assistance"
    definition_period = YEAR
    defined_for = StateCode.NM
    # A tax unit is eligible for base New Mexico Premium Assistance when the
    # program is in effect, at least one member is eligible for the federal ACA
    # premium tax credit, the tax unit files a federal return, and household
    # income is up to the federal poverty line limit.
    reference = (
        "https://api.realfile.rtsclients.com/PublicFiles/6c91aefc960e463485b3474662fd7fd2/15a6c1dd-e12b-4ffb-95af-bb54262218f3/FINAL-PY26%20%20MAP%20Policy%20and%20Procedures%20Manual.pdf#page=4",
        "https://api.realfile.rtsclients.com/PublicFiles/6c91aefc960e463485b3474662fd7fd2/15a6c1dd-e12b-4ffb-95af-bb54262218f3/FINAL-PY26%20%20MAP%20Policy%20and%20Procedures%20Manual.pdf#page=6",
        # 8.401.2.7(G) NMAC defines the FPL. The rule in force is one HTML page;
        # HCA's proposed amendment repeats the definition on PDF page 1.
        "https://prod-rf-lambda.rtssaas.com/PublicFiles/d89c47bd0d70402dba89b03a22bda6d1/45b8668e-460f-45cd-804f-92ee3d442343/8.401.2.html",
        "https://api.realfile.rtsclients.com/PublicFiles/6c91aefc960e463485b3474662fd7fd2/d3ee1d62-6f0f-4df7-b7fc-96a4c523ea89/08.401.0002_amended.pdf#page=1",
        # 45 CFR 155.300(a): the Exchange's FPL.
        "https://www.govinfo.gov/content/pkg/CFR-2025-title45-vol2/pdf/CFR-2025-title45-vol2-sec155-300.pdf#page=2",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nm.hca.premium_assistance
        in_effect = p.in_effect
        # At least one member must be eligible for the federal ACA PTC. This
        # gate embeds on-Marketplace enrollment (pays_aca_premium), the MFS
        # exclusion, and the 100-400% FPL required-contribution income test.
        aptc_eligible = add(tax_unit, period, ["is_aca_ptc_eligible"]) > 0
        # is_aca_ptc_eligible does not embed the federal PTC filing requirement
        # (IRC 36B(a); aca_ptc does), so gate it explicitly here, as aca_ptc
        # does.
        is_filer = tax_unit("files_return_for_aca_ptc", period)
        # The PY2026 manual excludes "consumers with household income over
        # 400% of the FPL". Test the exact ratio, not the truncated
        # aca_magi_fraction: truncation maps 400.00%-400.99% to 4.00, which
        # would admit incomes above 400%.
        # 8.401.2.7(G) NMAC defines the FPL as the level HHS issues "for the
        # applicable coverage year for the health insurance exchange". It names
        # no guideline year, and no New Mexico source defines family size, so
        # aca_fpg is a modeling choice on both points. Its prior-year guideline
        # is the one 45 CFR 155.300(a) has the Exchange use: the most recently
        # published when open enrollment starts. Its section 36B tax family
        # follows the program's federal PTC criteria (8.401.2.8(C)(1)(b) NMAC)
        # and leaves out a filer who can be claimed on another return.
        magi = max_(tax_unit("aca_magi", period), 0)
        fpg = tax_unit("aca_fpg", period)
        # Divide in float64: a float32 quotient can round a ratio just above
        # a limit down onto it.
        exact_magi_frac = magi.astype(np.float64) / fpg
        income_eligible = exact_magi_frac <= p.fpl_limit
        return in_effect & aptc_eligible & is_filer & income_eligible
