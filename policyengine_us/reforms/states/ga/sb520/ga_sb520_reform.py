from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_ga_sb520() -> Reform:
    class ga_standard_deduction(Variable):
        value_type = float
        entity = TaxUnit
        label = "Georgia standard deduction"
        unit = USD
        definition_period = YEAR
        reference = (
            "https://www.legis.ga.gov/api/legislation/document/20252026/242809#page=5",
        )
        defined_for = StateCode.GA

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.states.ga.tax.income.deductions.standard
            p_sb520 = parameters(period).gov.contrib.states.ga.sb520
            filing_status = tax_unit("filing_status", period)

            sb520_active = p_sb520.in_effect

            sb520_base = p_sb520.deductions.standard.amount[filing_status]
            sb520_threshold = p_sb520.deductions.standard.phase_out.threshold[
                filing_status
            ]
            sb520_rate = p_sb520.deductions.standard.phase_out.rate

            agi = tax_unit("adjusted_gross_income", period)
            excess_income = max_(agi - sb520_threshold, 0)
            phase_out_amount = excess_income * sb520_rate
            sb520_deduction = max_(sb520_base - phase_out_amount, 0)

            baseline_base = p.amount[filing_status]
            if p.applies:
                additional_standard = tax_unit(
                    "ga_additional_standard_deduction", period
                )
                baseline_deduction = baseline_base + additional_standard
            else:
                baseline_deduction = baseline_base

            return where(sb520_active, sb520_deduction, baseline_deduction)

    class ga_deductions(Variable):
        value_type = float
        entity = TaxUnit
        label = "Georgia deductions"
        unit = USD
        definition_period = YEAR
        reference = (
            # SB 520 Section 4 eliminates itemized deduction option
            "https://www.legis.ga.gov/api/legislation/document/20252026/242809#page=5",
        )
        defined_for = StateCode.GA

        def formula(tax_unit, period, parameters):
            p_sb520 = parameters(period).gov.contrib.states.ga.sb520

            sb520_active = p_sb520.in_effect

            # SB 520 Section 4 eliminates the option to itemize - standard deduction only
            sb520_deduction = tax_unit("ga_standard_deduction", period)

            # Baseline: itemize if federal itemizes
            itemizes = tax_unit("tax_unit_itemizes", period)
            sd = tax_unit("ga_standard_deduction", period)
            p = parameters(period).gov.irs.deductions
            itemized = add(tax_unit, period, p.itemized_deductions)
            baseline_deduction = where(itemizes, itemized, sd)

            return where(sb520_active, sb520_deduction, baseline_deduction)

    class ga_ctc(Variable):
        value_type = float
        entity = TaxUnit
        label = "Georgia Child Tax Credit"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.GA
        reference = (
            "https://www.legis.ga.gov/api/legislation/document/20252026/242809#page=6",
        )

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.states.ga.tax.income.credits.ctc
            p_sb520 = parameters(period).gov.contrib.states.ga.sb520

            sb520_active = p_sb520.in_effect

            person = tax_unit.members
            age = person("age", period)
            ctc_eligible_child = person("ctc_qualifying_child", period)
            # SB 520 preserves baseline GA CTC age threshold (under 6)
            ga_child_age_eligible = age < p.age_threshold
            eligible_children = tax_unit.sum(ctc_eligible_child & ga_child_age_eligible)

            sb520_amount = p_sb520.credits.ctc.amount
            baseline_amount = p.amount

            amount_per_child = where(sb520_active, sb520_amount, baseline_amount)
            return eligible_children * amount_per_child

    class ga_eitc(Variable):
        value_type = float
        entity = TaxUnit
        label = "Georgia Earned Income Tax Credit"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.GA
        reference = (
            "https://www.legis.ga.gov/api/legislation/document/20252026/242809#page=6",
        )

        def formula(tax_unit, period, parameters):
            p_sb520 = parameters(period).gov.contrib.states.ga.sb520

            sb520_active = p_sb520.in_effect

            federal_eitc = tax_unit("eitc", period)
            match_rate = p_sb520.credits.eitc.match

            ga_eitc_amount = federal_eitc * match_rate

            return where(sb520_active, ga_eitc_amount, 0)

    class ga_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        label = "Georgia refundable credits"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.GA

        def formula(tax_unit, period, parameters):
            p_sb520 = parameters(period).gov.contrib.states.ga.sb520

            sb520_active = p_sb520.in_effect

            ga_ctc_amount = tax_unit("ga_ctc", period)
            ga_eitc_amount = tax_unit("ga_eitc", period)

            sb520_refundable = ga_ctc_amount + ga_eitc_amount

            return where(sb520_active, sb520_refundable, 0)

    class ga_non_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        label = "Georgia non-refundable credits"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.GA

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.states.ga.tax.income.credits.non_refundable
            p_sb520 = parameters(period).gov.contrib.states.ga.sb520

            sb520_active = p_sb520.in_effect

            baseline_credits = add(tax_unit, period, p)

            ga_ctc_amount = tax_unit("ga_ctc", period)

            return where(
                sb520_active,
                max_(baseline_credits - ga_ctc_amount, 0),
                baseline_credits,
            )

    class ga_income_tax_before_non_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        label = "Georgia income tax before non-refundable credits"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.GA
        reference = (
            "https://www.legis.ga.gov/api/legislation/document/20252026/242809#page=3",
        )

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.states.ga.tax.income.main
            p_sb520 = parameters(period).gov.contrib.states.ga.sb520

            sb520_2027_active = p_sb520.brackets.in_effect

            filing_status = tax_unit("filing_status", period)
            status = filing_status.possible_values
            income = tax_unit("ga_taxable_income", period)

            sb520_tax = select(
                [
                    filing_status == status.SINGLE,
                    filing_status == status.SEPARATE,
                    filing_status == status.JOINT,
                    filing_status == status.HEAD_OF_HOUSEHOLD,
                    filing_status == status.SURVIVING_SPOUSE,
                ],
                [
                    p_sb520.brackets.single.calc(income),
                    p_sb520.brackets.separate.calc(income),
                    p_sb520.brackets.joint.calc(income),
                    p_sb520.brackets.head_of_household.calc(income),
                    p_sb520.brackets.surviving_spouse.calc(income),
                ],
            )

            baseline_tax = select(
                [
                    filing_status == status.SINGLE,
                    filing_status == status.SEPARATE,
                    filing_status == status.JOINT,
                    filing_status == status.HEAD_OF_HOUSEHOLD,
                    filing_status == status.SURVIVING_SPOUSE,
                ],
                [
                    p.single.calc(income),
                    p.separate.calc(income),
                    p.joint.calc(income),
                    p.head_of_household.calc(income),
                    p.surviving_spouse.calc(income),
                ],
            )

            return where(sb520_2027_active, sb520_tax, baseline_tax)

    class reform(Reform):
        def apply(self):
            self.update_variable(ga_standard_deduction)
            self.update_variable(ga_deductions)
            self.update_variable(ga_ctc)
            self.update_variable(ga_eitc)
            self.update_variable(ga_refundable_credits)
            self.update_variable(ga_non_refundable_credits)
            self.update_variable(ga_income_tax_before_non_refundable_credits)

    return reform


def create_ga_sb520_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_ga_sb520()

    p_sb520 = parameters.gov.contrib.states.ga.sb520

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        p_at_period = p_sb520(current_period)
        if p_at_period.in_effect or p_at_period.brackets.in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_ga_sb520()
    else:
        return None


ga_sb520 = create_ga_sb520_reform(None, None, bypass=True)
