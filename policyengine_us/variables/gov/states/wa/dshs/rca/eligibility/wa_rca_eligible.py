from policyengine_us.model_api import *


class wa_rca_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Washington Refugee Cash Assistance eligible"
    definition_period = MONTH
    defined_for = StateCode.WA
    reference = (
        "https://app.leg.wa.gov/wac/default.aspx?cite=388-400-0030",
        "https://app.leg.wa.gov/wac/default.aspx?cite=388-466-0120",
        "https://www.ecfr.gov/current/title-45/subtitle-B/chapter-IV/part-400/subpart-D/section-400.47",
        "https://www.ecfr.gov/current/title-45/subtitle-B/chapter-IV/part-400/subpart-J/section-400.211",
    )
    # Two WAC 388-400-0030 exclusions are not tracked at the moment:
    # (2)(b) applicants denied/terminated from TANF for noncompliance
    # (requires TANF sanction history) and (2)(c) full-time students in
    # higher education.
    #
    # NOTE on years_since_us_entry semantics: per 45 CFR 400.211(b), for
    # asylees and Cuban-Haitian entrants the ORR clock runs from the date
    # the qualifying status was granted, not from physical US entry. The
    # variable's own label ("Years since US entry or qualified immigration
    # status grant") acknowledges this — callers building inputs for those
    # populations should encode years-since-status-grant rather than
    # years-since-physical-entry.

    def formula(spm_unit, period, parameters):
        has_rca_eligible_member = (
            add(spm_unit, period, ["wa_rca_immigration_window_eligible"]) > 0
        )

        tanf_eligible = spm_unit("wa_tanf_eligible", period)
        sfa_eligible = spm_unit("wa_sfa_eligible", period)
        not_otherwise_eligible = ~tanf_eligible & ~sfa_eligible

        show_all = spm_unit("wa_show_all_cash_assistance_programs", period)

        income_eligible = spm_unit("wa_tanf_income_eligible", period)
        resources_eligible = spm_unit("wa_tanf_resources_eligible", period.this_year)

        return (
            (has_rca_eligible_member | show_all)
            & (not_otherwise_eligible | show_all)
            & income_eligible
            & resources_eligible
        )
