from policyengine_us.model_api import *


class ca_scc_general_assistance_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Eligible for Santa Clara County General Assistance"
    defined_for = "in_scc"
    reference = (
        "https://stgenssa.sccgov.org/debs/program_handbooks/general_assistance/assets/02Application/Application_Process.htm",
        "https://stgenssa.sccgov.org/debs/program_handbooks/general_assistance/assets/09Income/Potential_Inc_Res.htm",
    )

    def formula(spm_unit, period, parameters):
        # Per Chapter 2 (Eligibility for Other Programs — CalWORKs) and
        # Chapter 9 (Potential Income and Resources), households with a
        # minor child or pregnant adult must first apply for CalWORKs.
        # Only households that would not qualify for CalWORKs can fall
        # back to General Assistance.
        ca_tanf_eligible = spm_unit("ca_tanf_eligible", period.this_year)
        has_eligible_person = (
            add(spm_unit, period, ["ca_scc_general_assistance_eligible_person"]) > 0
        )
        income_eligible = spm_unit("ca_scc_general_assistance_income_eligible", period)
        return ~ca_tanf_eligible & has_eligible_person & income_eligible
