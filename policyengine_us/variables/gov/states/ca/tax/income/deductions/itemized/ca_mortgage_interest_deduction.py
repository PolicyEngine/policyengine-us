from policyengine_us.model_api import *
from policyengine_us.variables.household.expense.tax_unit.mortgage_interest_structure import (
    _debt_by_vintage,
)


class ca_mortgage_interest_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "California home mortgage interest deduction"
    unit = USD
    documentation = (
        "Home mortgage interest California allows on Schedule CA (540), Part "
        "II line 8. California does not apply IRC 163(h)(3)(F), so the "
        "pre-TCJA home acquisition and home equity debt limits apply "
        "regardless of when the debt was incurred."
    )
    reference = (
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=17225",
        "https://www.ftb.ca.gov/forms/2025/2025-540-ca-instructions.html",
        # PDF pages 9-11
        "https://www.irs.gov/pub/irs-prior/p936--2017.pdf#page=9",
    )
    definition_period = YEAR
    defined_for = StateCode.CA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ca.tax.income.deductions.itemized.interest
        p_federal = parameters(period).gov.irs.deductions.itemized.interest.mortgage
        filing_status = tax_unit("filing_status", period)
        # 2017 Publication 936, Table 1. Only grandfathered debt (line 1) is
        # treated differently by vintage; all later debt is line 2.
        grandfathered_debt, pre_tcja_debt, post_tcja_debt = _debt_by_vintage(
            [
                tax_unit("first_home_mortgage_balance", period),
                tax_unit("second_home_mortgage_balance", period),
            ],
            [
                tax_unit("first_home_mortgage_origination_year", period),
                tax_unit("second_home_mortgage_origination_year", period),
            ],
            p_federal.grandfathered_origination_year,
            p_federal.pre_tcja_origination_year,
        )
        # Line 9.
        debt = grandfathered_debt + pre_tcja_debt + post_tcja_debt
        # Lines 3-6. Grandfathered debt has no dollar limit but reduces the
        # home acquisition debt limit.
        acquisition_debt = min_(
            max_(grandfathered_debt, p.home_acquisition_debt_limit[filing_status]),
            debt,
        )
        # Line 7. Debt over the home acquisition debt limit may qualify as home
        # equity debt. The fair market value limit on home equity debt is not
        # modeled.
        home_equity_debt = min_(
            debt - acquisition_debt, p.home_equity_debt_limit[filing_status]
        )
        # Lines 8 and 11. Without a reported balance, the interest is treated
        # as within the limits, as in the federal calculation.
        deductible_share = np.divide(
            acquisition_debt + home_equity_debt,
            debt,
            out=np.ones_like(debt),
            where=debt > 0,
        )
        deductible_share = np.round(deductible_share, 3)
        # Line 10 uses total interest paid, before the federal debt limit.
        gross_interest = tax_unit("home_mortgage_interest_tax_unit", period)
        # A directly supplied federal deduction has already been limited, so
        # keep it when no gross interest is reported.
        federal_deduction = add(tax_unit, period, ["deductible_mortgage_interest"])
        return where(
            gross_interest > 0, gross_interest * deductible_share, federal_deduction
        )
