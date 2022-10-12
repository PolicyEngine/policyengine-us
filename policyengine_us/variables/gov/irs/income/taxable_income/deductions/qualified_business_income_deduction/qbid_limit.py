from policyengine_us.model_api import *


class qbid_limit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Qualified business income deduction limit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/199A#b_1"

    def formula(tax_unit, period, parameters):
        qbi = add(tax_unit, period, ["qualified_business_income"])
        w2_wages = add(tax_unit, period, ["w2_wages_from_qualified_business"])
        qualified_property = add(
            tax_unit, period, ["unadjusted_basis_qualified_property"]
        )
        taxable_income_less_qbid = tax_unit("taxable_income_less_qbid", period)
        qbid = parameters(period).gov.irs.deductions.qbi
        filing_status = tax_unit("filing_status", period)
        phase_out_start = qbid.phase_out.start[filing_status]
        phase_out_length = qbid.phase_out.length[filing_status]
        capped_phase_out_income = min_(
            phase_out_length,
            max_(0, taxable_income_less_qbid - phase_out_start),
        )
        percent_through_phase_out = capped_phase_out_income / phase_out_length
        income_based_deduction = qbid.max.rate * qbi
        w2_and_property_based_deduction = (
            qbid.max.w2_wages.alt_rate * w2_wages
            + qbid.max.business_property.rate * qualified_property
        )
        reduction = percent_through_phase_out * max_(
            0, income_based_deduction - w2_and_property_based_deduction
        )
        return tax_unit("maximum_qbid", period) - reduction
