from policyengine_us.model_api import *


class md_paa_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Maryland PAA eligible"
    definition_period = MONTH
    defined_for = StateCode.MD
    reference = (
        "https://dhs.maryland.gov/documents/FIA/Manuals/Public%20Assistance%20to%20Adults%20%28PAA%29%20Manual/PAA%20300%20Technical%20Eligibility%20rev%2011.22.docx",
        "https://regs.maryland.gov/us/md/exec/comar/07.03.07.03",
    )

    def formula(person, period, parameters):
        # COMAR 07.03.07.03(A)(2): applicants must be aged, blind, or
        # disabled and receive SSI, SSDI, or other federal cash benefit
        # on the basis of those criteria. SSI and SSDI receipt already
        # implies categorical qualification, so the aged/blind/disabled
        # gate only applies to the broader OASI / survivor and the
        # §300.5 / COMAR 07.03.07.03(G)(1) pending-application pathway,
        # which under COMAR additionally requires DHS to verify ABD
        # status before granting interim PAA — narrower than §300.5
        # standing alone. COMAR 07.03.07.03(A)(3) ("would-be SSI-eligible
        # except for income") is captured through the same
        # md_paa_pending_federal_benefit input — we don't auto-detect
        # income-denied SSI applicants at the moment, so the caller must
        # set the flag manually.
        receives_ssi = (person("ssi", period) > 0) | person("receives_ssi", period)
        ssdi = person("social_security_disability", period)
        receives_ssdi = ssdi > 0
        is_categorically_qualifying = person(
            "is_ssi_aged_blind_disabled", period.this_year
        )
        # `social_security` is the OASDI sum (retirement + survivors +
        # disability + dependents). Subtract SSDI so the OASI branch only
        # fires for non-SSDI Social Security receipt — SSDI already covers
        # itself via `receives_ssdi`.
        non_ssdi_oasi = person("social_security", period) - ssdi
        receives_other_oasdi_qualifying = (
            non_ssdi_oasi > 0
        ) & is_categorically_qualifying
        pending_federal_benefit = (
            person("md_paa_pending_federal_benefit", period)
            & is_categorically_qualifying
        )
        receives_federal_cash = (
            receives_ssi
            | receives_ssdi
            | receives_other_oasdi_qualifying
            | pending_federal_benefit
        )
        # PAA Manual §500: $2,000 resource limit. Each person's resources
        # are evaluated against the individual limit independently — the
        # couple limit ($3,000) is not used because PAA scopes eligibility
        # per recipient (one assistance unit per person), not per couple.
        # PAA's resource base also includes real property, money on hand,
        # trusts, and transfer-of-asset penalties — those refinements are
        # not tracked at the moment, so we approximate via
        # ssi_countable_resources.
        ssi_resource_limit = parameters(
            period
        ).gov.ssa.ssi.eligibility.resources.limit.individual
        ssi_resources = person("ssi_countable_resources", period.this_year)
        resource_eligible = ssi_resources <= ssi_resource_limit
        living_arrangement = person("md_paa_living_arrangement", period)
        in_facility = living_arrangement != living_arrangement.possible_values.NONE
        # MDH Rehabilitative Residence is a Title XIX medical-treatment-
        # facility setting per PAA Manual §900.3, so federal SSI is capped
        # at $30/mo per 42 USC § 1382(e)(1)(A). The caller must set
        # `ssi_lives_in_medical_treatment_facility` and
        # `ssi_medicaid_pays_majority_of_care` upstream so federal SSI is
        # computed correctly.
        is_rehab = (
            living_arrangement == living_arrangement.possible_values.REHAB_RESIDENCE
        )
        federal_la = person("ssi_federal_living_arrangement", period)
        is_medical_facility = (
            federal_la == federal_la.possible_values.MEDICAL_TREATMENT_FACILITY
        )
        # Bidirectional: REHAB iff SSI medical-facility. A CARE Home recipient
        # with the SSI medical-facility flag set would have federal SSI capped
        # at $30/mo and produce a wrong PAA cascade; conversely, REHAB without
        # the flag set would skip the cap. Either inconsistency makes the
        # person ineligible so the inputs are surfaced rather than silently
        # producing the wrong amount.
        facility_consistent = is_rehab == is_medical_facility
        return (
            receives_federal_cash
            & resource_eligible
            & in_facility
            & facility_consistent
        )
