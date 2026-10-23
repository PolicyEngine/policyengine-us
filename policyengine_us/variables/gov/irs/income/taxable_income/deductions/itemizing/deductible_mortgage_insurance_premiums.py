from policyengine_us.model_api import *


class deductible_mortgage_insurance_premiums(Variable):
    value_type = float
    entity = TaxUnit
    label = "Deductible mortgage insurance premiums"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Qualified mortgage insurance premiums treated as qualified residence "
        "interest under 26 U.S.C. 163(h)(3)(E), after the adjusted gross "
        "income phase-out (Schedule A line 8d). Publication 936 applies only "
        "the phase-out to premiums, not the qualified-loan-limit fraction that "
        "applies to interest and points."
    )
    reference = [
        "https://www.law.cornell.edu/uscode/text/26/163#h_3_E",
        "https://www.law.cornell.edu/uscode/text/26/163#h_3_F_i_III",
        "https://www.irs.gov/pub/irs-prior/i1040sca--2021.pdf#page=10",
        "https://www.irs.gov/pub/irs-prior/p936--2021.pdf#page=14",
    ]

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.irs.deductions.itemized.interest.mortgage_insurance_premiums
        premiums = add(
            tax_unit,
            period,
            [
                "mortgage_insurance_premiums",
                "second_residence_mortgage_insurance_premiums",
            ],
        )
        agi = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)
        # Worksheet lines 3-5: the deduction falls by the rate for each
        # increment, or fraction of one, of AGI above the start.
        excess = max_(0, agi - p.phase_out.start[filing_status])
        increments = np.ceil(excess / p.phase_out.increment[filing_status])
        reduction = min_(1, increments * p.phase_out.rate)
        return p.in_effect * premiums * (1 - reduction)
