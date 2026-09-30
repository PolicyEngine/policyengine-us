from policyengine_us.model_api import *


class nyc_income_tax_elimination_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the NYC income tax elimination credit"
    definition_period = YEAR
    reference = (
        "https://www.nysenate.gov/legislation/laws/TAX/1310",
        "https://www.tax.ny.gov/pdf/2025/inc/it270_2025_fill_in.pdf#page=1",
        "https://www.tax.ny.gov/pdf/2025/inc/it270i_2025.pdf#page=1",
    )
    defined_for = "in_nyc"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.local.ny.nyc.tax.income.credits.income_tax_elimination
        # § 1310(h)(1)(A); Form IT-270 line A: the taxpayer is entitled to a
        # dependent deduction under IRC § 151(c).
        has_dependent = tax_unit("tax_unit_dependents", period) > 0
        # § 1310(h)(1)(B) and (h)(2); line C: federal adjusted gross income
        # (§ 1310(h)(3)(B)) is no more than the phase-out width above the
        # threshold.
        agi = tax_unit("adjusted_gross_income", period)
        threshold = tax_unit(
            "nyc_income_tax_elimination_credit_income_threshold", period
        )
        income_eligible = agi <= threshold + p.phase_out_width
        # § 1310(h)(1)(D); line D: disqualified income as defined in
        # IRC § 32(i).
        investment_income = tax_unit("eitc_relevant_investment_income", period)
        investment_income_eligible = investment_income <= p.investment_income_limit
        # § 1310(h)(1)(C); line E: no New York State or City pass-through
        # entity tax credit.
        claims_ptet_credit = tax_unit(
            "ny_pass_through_entity_tax_credit_claimed", period
        )
        return (
            has_dependent
            & income_eligible
            & investment_income_eligible
            & ~claims_ptet_credit
        )
