from policyengine_us.model_api import *


class wa_wccc_smi_rate(Variable):
    value_type = float
    entity = SPMUnit
    label = "Washington WCCC State Median Income limit rate"
    definition_period = MONTH
    defined_for = StateCode.WA
    reference = (
        "https://app.leg.wa.gov/wac/default.aspx?cite=110-15-0005",
        "https://app.leg.wa.gov/wac/default.aspx?cite=110-15-0023",
        "https://app.leg.wa.gov/RCW/default.aspx?cite=43.216.814",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.wa.dcyf.wccc.eligibility.income.smi_rate

        person = spm_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        is_in_school = person("is_in_k12_school", period.this_year)
        # RCW 43.216.814 imposes the age 21 cap only on the HSE-certificate
        # path, which we don't track at the moment; the K-12 path has no
        # statutory age cap.
        is_teen_parent = is_head_or_spouse & is_in_school
        any_teen_parent = spm_unit.sum(is_teen_parent) > 0

        is_homeless = spm_unit.household("is_homeless", period.this_year)

        any_enrolled = spm_unit.sum(person("is_wccc_enrolled", period)) > 0

        is_applicant = ~is_homeless & ~any_teen_parent & ~any_enrolled
        return select(
            [is_homeless, any_teen_parent, any_enrolled, is_applicant],
            [p.homeless, p.teen_parent, p.recipient, p.applicant],
        )
