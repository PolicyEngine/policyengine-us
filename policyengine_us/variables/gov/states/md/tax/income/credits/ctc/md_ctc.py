from policyengine_us.model_api import *
from numpy import ceil


class md_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maryland Child Tax Credit"
    definition_period = YEAR
    unit = USD
    reference = (
        "https://mgaleg.maryland.gov/mgawebsite/Laws/StatuteText?article=gtg&section=10-751&enactments=false",
        "https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/instructions/2025/resident-booklet.pdf#page=27",
        "https://mgaleg.maryland.gov/2025RS/Chapters_noln/CH_604_hb0352e.pdf#page=169",  # Maryland House Bill 352 - Budget Reconciliation and Financing Act of 2025
    )
    defined_for = "md_ctc_eligible"

    def formula_2020(tax_unit, period, parameters):
        p = parameters(period).gov.states.md.tax.income.credits.ctc
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
        eligible = dependent & meets_age_limit
        eligible_children = tax_unit.sum(eligible)

        # Calculate base credit amount
        base_credit = eligible_children * p.amount

        # Apply federal CTC reduction if applicable
        if p.reduced_by_federal_credit:
            federal_ctc = tax_unit("ctc", period)
            base_credit = max_(base_credit - federal_ctc, 0)

        # Apply income-based phase-out instead of hard cutoff when phase-out applies
        if p.phase_out.applies:
            agi = tax_unit("adjusted_gross_income", period)

            # Calculate phase-out reduction: reduction for every increment (or fraction thereof) above threshold
            excess_income = max_(agi - p.phase_out.threshold, 0)
            # Use ceiling division: any fraction of increment counts as a full increment for phase-out
            increments_above_threshold = ceil(excess_income / p.phase_out.increment)
            phase_out_amount = (
                increments_above_threshold * p.phase_out.rate * eligible_children
            )

            # Worksheet 21C applies the reduction to each qualifying child.
            # Apply phase-out (credit cannot go below zero)
            return max_(base_credit - phase_out_amount, 0)

        return base_credit
