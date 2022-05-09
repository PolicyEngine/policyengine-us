from openfisca_us.model_api import *


class qualified_business_income_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Qualified business income deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/199A#b_1"

    def formula(tax_unit, period, parameters):
        qbi = tax_unit("qualified_business_income", period)
        w2_wages = tax_unit("w2_wages_from_qualified_business", period)
        qualified_property = tax_unit("unadjusted_basis_qualified_property", period)
        taxable_income_less_qbid = tax_unit("taxable_income_less_qbid", period)
        qbid = parameters(period).irs.deductions.qbi
        max_qbid = tax_unit("maximum_qbid", period)
        filing_status = tax_unit("filing_status", period)
        between_thresholds = (
            (taxable_income_less_qbid >= qbid.phaseout.start)
            & (taxable_income_less_qbid < qbid.phaseout.start + qbid.phaseout.length)
        )

        capped_phaseout_income = min_(qbi.phaseout.length, max_(0, taxable_income_less_qbid))
        percent_through_phaseout = capped_phaseout_income / qbi.phaseout.length
        income_based_deduction = qbid.max.rate * qbi
        w2_and_property_based_deduction = (
            qbid.max.w2_wages.alt_rate * w2_wages
            + qbid.max.business_property.rate * qualified_property
        )
        income_based_deduction_reduction = percent_through_phaseout * max_(0, income_based_deduction - w2_and_property_based_deduction)
        reduced_deduction = income_based_deduction - income_based_deduction_reduction
        return where(between_thresholds, max_qbid - reduced_deduction, max_qbid)



