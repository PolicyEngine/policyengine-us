from policyengine_us.model_api import *


class md_ctc_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Maryland Child Tax Credit"
    definition_period = YEAR
    reference = (
        "https://mgaleg.maryland.gov/mgawebsite/Laws/StatuteText?article=gtg&section=10-751&enactments=false",
        "https://mgaleg.maryland.gov/2025RS/Chapters_noln/CH_604_hb0352e.pdf#page=169",  # Maryland House Bill 352 - Budget Reconciliation and Financing Act of 2025
    )
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.md.tax.income.credits.ctc
        agi = tax_unit("adjusted_gross_income", period)

        # Check for qualifying children (used in both paths)
        person = tax_unit.members
        # § 10-751(a)(2)(i): a qualified child is "a dependent for purposes of
        # § 152 of the Internal Revenue Code"; under IRC 152(b)(1) a return on
        # which the filer (or, if joint, either spouse) can be claimed has none.
        filer_is_dependent = person.tax_unit(
            "head_or_spouse_is_dependent_elsewhere", period
        )
        dependent = person("is_tax_unit_dependent", period) & ~filer_is_dependent
        disabled = person("is_disabled", period)
        age_limit = where(disabled, p.age_threshold.disabled, p.age_threshold.main)
        meets_age_limit = person("age", period) < age_limit
        qualifying_child = dependent & meets_age_limit
        has_qualifying_child = tax_unit.sum(qualifying_child) > 0

        # When phase-out applies (2025+): must have qualifying child AND AGI below max_agi
        # Per Worksheet 21C: "$24,000 or less" is eligible; "$24,001 or greater, STOP."
        # max_agi is set to 24_001 so that agi < 24_001 includes $24,000.
        agi_eligible = agi < p.phase_out.max_agi
        phase_out_eligible = has_qualifying_child & agi_eligible

        # When phase-out does not apply (pre-2025): use old logic (hard AGI cutoff)
        pre_phase_out_eligible = agi <= p.agi_cap

        return where(p.phase_out.applies, phase_out_eligible, pre_phase_out_eligible)
