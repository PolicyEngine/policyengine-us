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
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.wa.dcyf.wccc.eligibility.income.smi_rate
        teen_age_limit = parameters(
            period
        ).gov.states.wa.dcyf.wccc.eligibility.age_threshold.teen_parent

        person = spm_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        age = person("age", period.this_year)
        is_in_school = person("is_in_k12_school", period.this_year)
        # We don't track HSE participation at the moment; this captures only
        # the K-12 path for the teen parent income tier.
        is_teen_parent = is_head_or_spouse & (age < teen_age_limit) & is_in_school
        any_teen_parent = spm_unit.sum(is_teen_parent) > 0

        is_homeless = spm_unit.household("is_homeless", period.this_year)

        any_enrolled = spm_unit.sum(person("is_wccc_enrolled", period)) > 0

        return select(
            [is_homeless, any_teen_parent, any_enrolled],
            [p.homeless, p.teen_parent, p.recipient],
            default=p.applicant,
        )
