from policyengine_us.model_api import *


class oh_ccap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Ohio CCAP based on income"
    definition_period = MONTH
    defined_for = StateCode.OH
    reference = (
        "https://dam.assets.ohio.gov/image/upload/childrenandyouth.ohio.gov/For%20Partners/Rules%20and%20Resources/2025/PL_21.pdf#page=2",
        "https://codes.ohio.gov/ohio-administrative-code/rule-5180:2-16-03",
    )

    def formula(spm_unit, period, parameters):
        # DCY Procedure Letter 21: initial (intake) eligibility caps family
        # income at 145% of the federal poverty guideline; once enrolled, a
        # family remains eligible until income exceeds 300% FPG. A family with
        # a special-needs child uses a 150% FPG initial limit.
        p = parameters(period).gov.states.oh.dcy.ccap.income.fpl_rate
        countable_income = spm_unit("oh_ccap_countable_income", period)
        # spm_unit_fpg is YEAR-defined; the bare period auto-divides to monthly.
        fpg = spm_unit("spm_unit_fpg", period)
        person = spm_unit.members
        has_special_needs_child = (
            spm_unit.sum(
                person("oh_ccap_eligible_child", period)
                & person("has_developmental_delay", period.this_year)
            )
            > 0
        )
        # A special-needs child raises the initial limit to 150% FPG.
        initial_limit = fpg * where(
            has_special_needs_child,
            p.special_needs_eligibility,
            p.initial_eligibility,
        )
        enrolled = spm_unit("oh_ccap_enrolled", period)
        income_limit = where(enrolled, fpg * p.ongoing_eligibility, initial_limit)
        fpl_eligible = countable_income <= income_limit
        # Families enrolled in Ohio Works First (TANF) are categorically
        # income-eligible. Using is_tanf_enrolled (rather than computed TANF
        # eligibility) breaks the CCAP-TANF circular dependency.
        is_tanf = spm_unit("is_tanf_enrolled", period)
        return is_tanf | fpl_eligible
