from policyengine_us.model_api import *


class ia_ssa_ihhrc_participation(Variable):
    value_type = float
    entity = Person
    label = "Iowa SSA in-home health-related care client participation"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.IA
    reference = (
        # 441 IAC 177.2(1)"f"-"g" and 177.8(2) (IAC 8/5/26)
        "https://www.legis.iowa.gov/docs/iac/chapter/441.177.pdf#page=1",
        # 441 IAC 177.4(1)"f"-"g" and 177.10(2) (IAC 2/5/25); PDF pages 2, 4-5
        "https://www.legis.iowa.gov/docs/iac/chapter/01-07-2026.441.177.pdf#page=2",
        # PDF pages 41-44, 49
        "https://hhs.iowa.gov/media/3987/download?inline=#page=41",
    )

    def formula(person, period, parameters):
        # 6-B Home Maintenance Allowance (IHHRC) prints the SSI individual and
        # couple standards ($994 and $1,491) and gives the couple allowance
        # "even if only one spouse receives in-home health-related care", so
        # the federal benefit rates are used and an SSI reform carries over.
        # A child has no spouse and receives the individual standard.
        ssi = parameters(period).gov.ssa.ssi
        income = person("ia_ssa_care_countable_income", period)
        deductions = max_(person("ia_ssa_care_additional_deductions", period), 0)
        has_spouse = person("ia_ssa_has_spouse", period)
        maintenance = where(has_spouse, ssi.amount.couple, ssi.amount.individual)
        deductions = where(has_spouse, person.marital_unit.sum(deductions), deductions)
        # 441 IAC 177.2(1)"f"(3) disregards "The amount of the SSI standard for
        # a dependent plus any established unmet medical needs for each
        # dependent living in the home. Any income of the dependent shall be
        # applied to the dependent's needs before making this disregard." 6-B
        # Home Maintenance Allowance (IHHRC) allows "$ 497 Maximum additional
        # allowance for each dependent" less the dependent's income. SSI's
        # ineligible child allocation is that amount, summed over the tax unit
        # as in SSI spousal deeming. A child recipient's siblings are allowed in
        # parental deeming instead (177.2(1)"g"(1)).
        # NOTE: 6-B p.42 lists the "Home maintenance allowance for a single
        # person, or for a couple if there is a spouse living with the client
        # or a dependent living with an eligible person", with no deduction of
        # the dependent's income. 441 IAC 177.2(1)"f"(3) applies "Any income of
        # the dependent ... to the dependent's needs before making this
        # disregard", as 6-B p.43 does ("Subtract a dependent's income"; Mr. B,
        # 1,400 - 994 - 372 = 34). The model follows the rule and p.43
        # (ia_ssa.yaml Case 62).
        head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        dependents = head_or_spouse * person.tax_unit.sum(
            person("ssi_ineligible_child_allocation", period)
        )
        participation = max_(income - maintenance - dependents - deductions, 0)
        # No client participation is required in a first partial month.
        return where(
            person("ia_ssa_care_initial_partial_month", period), 0, participation
        )
