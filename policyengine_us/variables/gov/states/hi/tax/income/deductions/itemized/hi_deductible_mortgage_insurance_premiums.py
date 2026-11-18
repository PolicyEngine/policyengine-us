from policyengine_us.model_api import *


class hi_deductible_mortgage_insurance_premiums(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii deductible mortgage insurance premiums"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.HI
    reference = (
        "https://files.hawaii.gov/tax/news/announce/ann21-01.pdf",
        "https://files.hawaii.gov/tax/legal/legis/2021/21digest.pdf#page=9",
        "https://data.capitol.hawaii.gov/hrscurrent/Vol04_Ch0201-0257/HRS0235/HRS_0235-0002_0004.htm",
    )
    documentation = (
        "Qualified mortgage insurance premiums on the first and second home, "
        "after the federal worksheet's phase-out using Hawaii adjusted gross "
        "income. HRS 235-2.4(j) does not adopt IRC 163(h)(3)(F), including "
        "the federal restoration of premiums from 2026."
    )

    def formula(tax_unit, period, parameters):
        in_effect = parameters(
            period
        ).gov.states.hi.tax.income.deductions.itemized.mortgage_insurance_premiums.in_effect
        if not in_effect:
            return 0
        p = parameters(
            period
        ).gov.irs.deductions.itemized.interest.mortgage_insurance_premiums.phase_out
        premiums = add(
            tax_unit,
            period,
            [
                "mortgage_insurance_premiums",
                "second_residence_mortgage_insurance_premiums",
            ],
        )
        agi = tax_unit("hi_agi", period)
        filing_status = tax_unit("filing_status", period)
        excess = max_(0, agi - p.start[filing_status])
        increments = np.ceil(excess / p.increment[filing_status])
        reduction = min_(1, increments * p.rate)
        return in_effect * premiums * (1 - reduction)
