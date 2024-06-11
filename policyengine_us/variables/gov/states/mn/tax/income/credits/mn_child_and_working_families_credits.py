from policyengine_us.model_api import *


class mn_child_and_working_families_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota child and working families credits"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/290.0661#stat.290.0661.4"
        "https://www.revisor.mn.gov/statutes/cite/290.0671"
        "https://www.revenue.state.mn.us/sites/default/files/2024-01/m1cwfc-23_1.pdf"
    )
    defined_for = StateCode.MN

    def formula(tax_unit, period, parameters):
        # Minnesota combines the Child Tax Credit and
        # the Working Family Credit into a single credit
        # The credits are defined by separate legal code sections
        # but are calculated together in the tax forms.
        # Child Tax Credit computation:
        qualifying_children = tax_unit("ctc_qualifying_children", period)
        p = parameters(period).gov.states.mn.tax.income.credits.cwfc
        base_ctc_amount = qualifying_children * p.ctc.amount
        # Working Family Credit computation:
        wfc_eligible = tax_unit("mn_wfc_eligible", period)
        # The credit is phased in based on earnings
        earnings = tax_unit("filer_adjusted_earnings", period)
        base_wfc_credit = p.wfc.phase_in.calc(earnings)
        person = tax_unit.members
        qualifying_child = person("is_child_dependent", period)
        age = person("age", period)
        full_time_student = person("is_full_time_student", period)
        qualifying_older_child = (
            qualifying_child
            & (age > p.wfc.additional.age_threshold)
            & full_time_student
        )
        qualifying_older_children = tax_unit.sum(qualifying_older_child)
        additional_wfc_credit = p.wfc.additional.amount.calc(
            qualifying_older_children
        )
        base_wfc_amount = (
            base_wfc_credit + additional_wfc_credit
        ) * wfc_eligible
        # The credit amounts are combined and phase out together based on the number of
        # qualifying older children
        combined_credit = base_ctc_amount + base_wfc_amount
        # The phase out threshold is based on the larger of AGI and earnings and filing status
        agi = tax_unit("adjusted_gross_income", period)
        income = max_(earnings, agi)
        filing_status = tax_unit("filing_status", period)
        phase_out_threshold = where(
            filing_status == filing_status.possible_values.JOINT,
            p.phase_out.threshold.joint,
            p.phase_out.threshold.other,
        )
        excess_income = max_(0, income - phase_out_threshold)
        # Minnesota applies a different phase out rate for filers ineligible for the Child Tax Credit
        # with qualifying older children for the WFC
        lower_phase_out_rate_eligible = (qualifying_older_children > 0) & (
            base_ctc_amount == 0
        )
        phase_out_rate = where(
            lower_phase_out_rate_eligible,
            p.phase_out.rate.ctc_ineligible_with_qualifying_older_children,
            p.phase_out.rate.main,
        )
        reduction = excess_income * phase_out_rate
        return max_(0, combined_credit - reduction)
