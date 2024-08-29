from policyengine_us.model_api import *


# Repealing Minnesota Bill HF1938 to pre 2023 rules
def create_mn_walz_hf1938_repeal() -> Reform:
    class mn_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        label = "Minnesota refundable income tax credits"
        unit = USD
        definition_period = YEAR
        reference = (
            "https://www.revenue.state.mn.us/sites/default/files/2023-01/m1ref_21.pdf"
            "https://www.revenue.state.mn.us/sites/default/files/2023-01/m1ref_22.pdf"
        )
        defined_for = StateCode.MN

        def formula(tax_unit, period, parameters):
            if period.start.year >= 2023:
                instant_str = f"2022-01-01"
            else:
                instant_str = period
            p = parameters(instant_str).gov.states.mn.tax.income.credits
            return add(tax_unit, period, p.refundable)

    class mn_social_security_subtraction(Variable):
        value_type = float
        entity = TaxUnit
        label = "Minnesota social security subtraction"
        unit = USD
        definition_period = YEAR
        reference = (
            "https://www.taxformfinder.org/forms/2021/2021-minnesota-form-m1m.pdf"
            "https://www.revenue.state.mn.us/sites/default/files/2023-01/m1m_22.pdf"
        )
        defined_for = StateCode.MN

        def formula(tax_unit, period, parameters):
            # specify parameters
            filing_status = tax_unit("filing_status", period)
            p = parameters(
                period
            ).gov.states.mn.tax.income.subtractions.social_security
            total_benefit_fraction = p.total_benefit_fraction
            income_amount = p.income_amount[filing_status]
            net_income_fraction = p.net_income_fraction
            alt_amount = p.alternative_amount[filing_status]
            # calculate subtraction amount (following "Worksheet for line 12")
            # ... US-taxable social security benefits
            us_taxable_oasdi = add(
                tax_unit, period, ["taxable_social_security"]
            )
            # ... alternative benefit subtraction amount
            us_gross_income = add(tax_unit, period, ["irs_gross_income"])
            adj_income = us_gross_income - us_taxable_oasdi
            total_oasdi = add(tax_unit, period, ["social_security"])
            oasdi_amount = total_oasdi * total_benefit_fraction
            tax_exempt_int = add(
                tax_unit, period, ["tax_exempt_interest_income"]
            )
            sum_income = adj_income + oasdi_amount + tax_exempt_int
            us_ald = tax_unit("above_the_line_deductions", period)
            student_loan_int = add(tax_unit, period, ["student_loan_interest"])
            mn_ald = max_(0, us_ald - student_loan_int)
            income = max_(0, sum_income - mn_ald)
            net_income = max_(0, income - income_amount)
            alt_sub_amt = max_(
                0, alt_amount - (net_income * net_income_fraction)
            )
            return min_(us_taxable_oasdi, alt_sub_amt)

    class mn_standard_deduction(Variable):
        value_type = float
        entity = TaxUnit
        label = "Minnesota standard deduction"
        unit = USD
        definition_period = YEAR
        reference = (
            "https://www.revenue.state.mn.us/sites/default/files/2023-01/m1_inst_21.pdf"
            "https://www.revenue.state.mn.us/sites/default/files/2023-03/m1_inst_22.pdf"
        )
        defined_for = StateCode.MN

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.states.mn.tax.income.deductions.standard
            # ... calculate pre-limitation amount
            filing_status = tax_unit("filing_status", period)
            base_amt = p.base[filing_status]
            aged_blind_count = tax_unit("aged_blind_count", period)
            extra_amt = aged_blind_count * p.extra[filing_status]
            std_ded = base_amt + extra_amt
            # ... calculate standard deduction offset
            std_ded_offset = p.reduction.alternate.rate * std_ded
            agi = tax_unit("adjusted_gross_income", period)
            excess_agi = max_(
                0, agi - p.reduction.agi_threshold.low[filing_status]
            )
            excess_agi_offset = (
                p.reduction.excess_agi_fraction.low * excess_agi
            )
            offset = min_(std_ded_offset, excess_agi_offset)
            return max_(0, std_ded - offset)

    class mn_itemized_deductions(Variable):
        value_type = float
        entity = TaxUnit
        label = "Minnesota itemized deductions"
        unit = USD
        definition_period = YEAR
        reference = (
            "https://www.revenue.state.mn.us/sites/default/files/2021-12/m1_21_0.pdf"
            "https://www.revenue.state.mn.us/sites/default/files/2023-01/m1_inst_21.pdf"
            "https://www.revenue.state.mn.us/sites/default/files/2022-12/m1_22.pdf"
            "https://www.revenue.state.mn.us/sites/default/files/2023-03/m1_inst_22.pdf"
        )
        defined_for = StateCode.MN

        def formula(tax_unit, period, parameters):
            # 2021 Form M1 instructions say:
            #   You may claim the Minnesota standard deduction or itemize
            #   your deductions on your Minnesota return. You will generally
            #   pay less Minnesota income tax if you take the larger of your
            #   itemized or standard deduction.
            # ... calculate pre-limitation itemized deductions
            itm_deds_less_salt = tax_unit(
                "itemized_deductions_less_salt", period
            )
            capped_property_taxes = tax_unit("capped_property_taxes", period)
            mn_itm_deds = itm_deds_less_salt + capped_property_taxes
            # ... calculate itemized deductions offset
            p = parameters(period).gov.states.mn.tax.income.deductions.itemized
            exempt_deds = add(
                tax_unit,
                period,
                ["medical_expense_deduction", "casualty_loss_deduction"],
            )
            net_deds = max_(0, mn_itm_deds - exempt_deds)
            net_deds_offset = p.reduction.alternate.rate * net_deds
            agi = tax_unit("adjusted_gross_income", period)
            filing_status = tax_unit("filing_status", period)
            excess_agi = max_(
                0, agi - p.reduction.agi_threshold.low[filing_status]
            )
            excess_agi_offset = (
                p.reduction.excess_agi_fraction.low * excess_agi
            )
            offset = min_(net_deds_offset, excess_agi_offset)
            return max_(0, mn_itm_deds - offset)

    class mn_cdcc(Variable):
        value_type = float
        entity = TaxUnit
        label = "Minnesota child and dependent care expense credit"
        unit = USD
        definition_period = YEAR
        reference = (
            "https://www.revenue.state.mn.us/sites/default/files/2023-02/m1cd_21.pdf"
            "https://www.revenue.state.mn.us/sites/default/files/2023-01/m1cd_22_0.pdf"
        )
        defined_for = StateCode.MN

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.states.mn.tax.income.credits.cdcc
            person = tax_unit.members
            # determine eligibility for Minnesota CDCC
            filing_status = tax_unit("filing_status", period)
            eligible = filing_status != filing_status.possible_values.SEPARATE
            # calculate number of qualifying dependents
            # ... children
            age = person("age", period)
            qualifies_by_age = age < p.child_age
            # ... disability
            non_head = ~person("is_tax_unit_head", period)
            disabled = person("is_incapable_of_self_care", period)
            qualifies_by_disability = non_head & disabled
            dep_count = tax_unit.sum(
                qualifies_by_age | qualifies_by_disability
            )
            # calculate qualifying care expenses
            expense = tax_unit("tax_unit_childcare_expenses", period)
            # ... cap expense by number of qualifying dependents
            eligible_count = min_(dep_count, p.maximum_dependents)
            expense = min_(expense, p.maximum_expense * eligible_count)
            # ... cap expense by lower earnings of head and spouse if present
            expense = min_(expense, tax_unit("min_head_spouse_earned", period))
            # calculate pre-phaseout credit amount
            agi = tax_unit("adjusted_gross_income", period)
            pre_po_amount = expense * p.expense_fraction.calc(agi)
            # calculate post-phaseout credit amount
            excess_agi = max_(0, agi - p.phaseout_threshold)
            po_amount = excess_agi * p.phaseout_rate
            amount = max_(0, pre_po_amount - po_amount)
            # credit amount only for eligibles
            return eligible * amount

    class reform(Reform):
        def apply(self):
            self.neutralize_variable("mn_public_pension_subtraction")
            self.update_variable(mn_social_security_subtraction)
            self.update_variable(mn_refundable_credits)
            self.update_variable(mn_standard_deduction)
            self.update_variable(mn_itemized_deductions)
            self.update_variable(mn_cdcc)

    return reform


def create_mn_walz_hf1938_repeal_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_mn_walz_hf1938_repeal()

    p = parameters(period).gov.contrib.states.mn.walz.hf1938

    if p.repeal:
        return create_mn_walz_hf1938_repeal()
    else:
        return None


mn_walz_hf1938 = create_mn_walz_hf1938_repeal_reform(None, None, bypass=True)
