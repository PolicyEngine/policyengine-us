from policyengine_us.model_api import *


class md_paa_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Maryland PAA eligible"
    definition_period = MONTH
    defined_for = StateCode.MD
    reference = (
        "https://dhs.maryland.gov/documents/FIA/Manuals/Public%20Assistance%20to%20Adults%20%28PAA%29%20Manual/PAA%20300%20Technical%20Eligibility%20rev%2011.22.docx",
        "https://www.law.cornell.edu/regulations/maryland/COMAR-07-03-07-03",
    )

    def formula(person, period, parameters):
        # PAA Manual §300.1.B / COMAR 07.03.07.03: applicants must be aged,
        # blind, or disabled and receive SSI, SSDI, or other federal cash
        # benefit on the basis of those criteria. SSI and SSDI receipt
        # already implies categorical qualification, so the aged/blind/
        # disabled gate only applies to the broader OASI / survivor and
        # the §300.5 pending-application / no-fault-denial pathways.
        receives_ssi = person("ssi", period) > 0
        receives_ssdi = person("social_security_disability", period) > 0
        is_categorically_qualifying = person(
            "is_ssi_aged_blind_disabled", period.this_year
        )
        receives_other_oasdi_qualifying = (
            person("social_security", period) > 0
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
        # PAA Manual §500.2.B: $2,000 resource limit (parity with federal SSI
        # individual limit). Couple cases are evaluated per-person. PAA's
        # resource base also includes real property, money on hand, trusts,
        # transfer-of-asset penalties (§500.4) — those refinements are not
        # tracked at the moment, so we approximate via ssi_countable_resources.
        ssi_resource_limit = parameters(
            period
        ).gov.ssa.ssi.eligibility.resources.limit.individual
        ssi_resources = person("ssi_countable_resources", period.this_year)
        resource_eligible = ssi_resources <= ssi_resource_limit
        living_arrangement = person("md_paa_living_arrangement", period)
        in_facility = living_arrangement != living_arrangement.possible_values.NONE
        return receives_federal_cash & resource_eligible & in_facility
