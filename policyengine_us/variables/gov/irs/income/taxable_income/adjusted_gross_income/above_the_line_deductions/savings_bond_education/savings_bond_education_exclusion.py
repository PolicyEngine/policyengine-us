from policyengine_us.model_api import *


class savings_bond_education_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    label = "Excludable savings bond interest used for higher education"
    documentation = "Form 8815 lines 4-14: interest times qualified expenses over proceeds (at most 1), phased out by modified AGI; none on a separate return."
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/135",
        "https://www.irs.gov/pub/irs-pdf/f8815.pdf",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.savings_bond_education_exclusion
        expenses = max_(
            0,
            tax_unit("savings_bond_education_qualified_expenses", period)
            - tax_unit("savings_bond_education_nontaxable_benefits", period),
        )
        proceeds = tax_unit("savings_bond_redemption_proceeds", period)
        interest = max_(0, tax_unit("savings_bond_redemption_interest", period))
        ratio = np.clip(
            np.divide(
                expenses, proceeds, out=np.zeros_like(expenses), where=proceeds > 0
            ),
            0,
            1,
        )
        tentative = interest * ratio
        filing_status = tax_unit("filing_status", period)
        start = p.phase_out.start[filing_status]
        length = p.phase_out.length[filing_status]
        magi = tax_unit("savings_bond_education_exclusion_magi", period)
        reduction = np.clip((magi - start) / length, 0, 1)
        separate = filing_status == filing_status.possible_values.SEPARATE
        allowed = ~separate | p.available_married_filing_separately
        return allowed * tentative * (1 - reduction)
