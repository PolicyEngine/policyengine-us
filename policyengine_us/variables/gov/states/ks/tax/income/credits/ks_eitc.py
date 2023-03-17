from policyengine_us.model_api import *


class ks_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "KS EITC amount"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ksrevenue.gov/pdf/k-4021.pdf"
        "https://www.ksrevenue.gov/pdf/ip21.pdf"
        "https://www.ksrevenue.gov/pdf/k-4022.pdf"
        "https://www.ksrevenue.gov/pdf/ip22.pdf"
    )
    defined_for = StateCode.KS

    """
    def formula(tax_unit, period, parameters):
        branch = get_ks_eitc_branch(tax_unit, period, parameters)
        ks_eitc = parameters.gov.states.ca.tax.income.credits.earned_income
        current_ks_eitc = ks_eitc(period)
        amount = (
            branch.calculate("earned_income_tax_credit", period)
            * current_ks_eitc.adjustment.factor
        )
        eligible = branch.calculate("eitc_eligible", period)
        second_phase_out_start = tax_unit(
            "ks_eitc_second_phase_out_start", period
        )
        second_phase_out_end = current_ks_eitc.phase_out.final.end
        count_children = tax_unit("eitc_child_count", period)
        eitc_at_second_phase_out_start = (
            current_ks_eitc.phase_out.final.start.calc(count_children)
        ) * eligible
        earned_income = tax_unit("filer_earned", period)
        amount_along_second_phase_out = earned_income - second_phase_out_start
        second_phase_out_width = second_phase_out_end - second_phase_out_start
        percent_along_second_phase_out = (
            amount_along_second_phase_out / second_phase_out_width
        )
        eitc_along_second_phase_out = max_(
            (eitc_at_second_phase_out_start)
            * (1 - percent_along_second_phase_out),
            0,
        )

        is_on_second_phase_out = earned_income >= second_phase_out_start

        return where(
            is_on_second_phase_out,
            eitc_along_second_phase_out,
            amount,
        )
    """
