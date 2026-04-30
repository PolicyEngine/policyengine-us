from policyengine_us.model_api import *


class wa_sfa_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Washington State Family Assistance eligible"
    definition_period = MONTH
    defined_for = StateCode.WA
    reference = (
        # WAC 388-400-0010(1)-(2): umbrella SFA eligibility subsections.
        "https://app.leg.wa.gov/wac/default.aspx?cite=388-400-0010",
    )

    def formula(spm_unit, period, parameters):
        # Pathway A: qualified alien in 5-year bar, per WAC 388-400-0010(2)(a).
        # Per WAC 388-400-0010, SFA is for families federally ineligible for
        # TANF. Exclude at SPM-unit level to prevent mixed-status households
        # from receiving both.
        has_sfa_eligible_immigrant = (
            add(spm_unit, period, ["wa_sfa_immigration_status_eligible"]) > 0
        )
        has_tanf_eligible_immigrant = (
            add(spm_unit, period, ["wa_tanf_immigration_status_eligible"]) > 0
        )
        immigration_pathway = has_sfa_eligible_immigrant & ~has_tanf_eligible_immigrant

        # Pathway B: 19-20 year old student, per WAC 388-400-0010(2)(c) and
        # the caretaker relative of such a student per (2)(d). Caretakers
        # are covered automatically because the student's presence in the
        # SPM unit makes the whole unit demographically eligible.
        has_19_20_student = (
            add(spm_unit, period, ["wa_sfa_student_pathway_eligible"]) > 0
        )
        tanf_eligible = spm_unit("wa_tanf_eligible", period)
        student_pathway = has_19_20_student & ~tanf_eligible

        federal_demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)
        demographic_eligible = federal_demographic_eligible | has_19_20_student

        show_all = spm_unit("wa_show_all_cash_assistance_programs", period)
        income_eligible = spm_unit("wa_tanf_income_eligible", period)
        resources_eligible = spm_unit("wa_tanf_resources_eligible", period.this_year)
        return (
            demographic_eligible
            & (immigration_pathway | student_pathway | show_all)
            & income_eligible
            & resources_eligible
        )
