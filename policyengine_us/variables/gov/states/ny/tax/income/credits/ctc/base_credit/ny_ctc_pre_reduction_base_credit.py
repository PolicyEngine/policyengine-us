from policyengine_us.model_api import *


class ny_ctc_pre_reduction_base_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "The base NY CTC credit before reduction"
    documentation = "New York's Empire State Child Credit Worksheet A / B Part 1"
    unit = USD
    definition_period = YEAR
    reference = "https://www.tax.ny.gov/pdf/2021/inc/it213i_2021.pdf"
    defined_for = StateCode.NY


    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ny.tax.income.credits.ctc
        person = tax_unit.members
        # Qualifying children
        ctc_qualifying_child = person("ctc_qualifying_child", period)
        qualifying_children = tax_unit.sum(ctc_qualifying_child)
        base_credit = qualifying_children * p.amount.base
        # New York recomputed FAGI - use normal FAGI
        fagi = tax_unit("adjusted_gross_income", period)
        # AGI is increased by cretain exclusions if claimed additional credits
        claimed_additional_credits = tax_unit("ny_ctc_claimed_additional_credits", period)
        total_exclusions = add(tax_unit, period, ["foreign_earned_income_exclusion", "puerto_rico_income"])
        agi_with_exclusion_amount = where(claimed_additional_credits, total_exclusions + fagi, fagi)
        # Federal CTC phase out threshold
        federal_threshold = gov.irs.credits.ctc.phase_out.threshold[
            tax_unit("filing_status", period)
        ]
        agi_over_threshold = agi_with_exclusion_amount > federal_threshold
        # The reduced AGI is rounded up to the nearest NY CTC base amount
        rounded_reduced_agi_multiple = np.ceil(agi_with_exclusion_amount - federal_threshold / p.amount.base)
        rounded_reduced_agi_amount =rounded_reduced_agi_multiple * p.amount.base
        rounded_reduced_agi = where(agi_over_threshold, rounded_reduced_agi_amount, 0)
        # The base credit is reduced by a fraction of the reduced AGI
        subtraction_amount = rounded_reduced_agi * p.amount.match
        return max_(base_credit - subtraction_amount, 0)
