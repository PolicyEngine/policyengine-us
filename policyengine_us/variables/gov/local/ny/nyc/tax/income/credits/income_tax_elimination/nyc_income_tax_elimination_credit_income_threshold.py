from policyengine_us.model_api import *


class nyc_income_tax_elimination_credit_income_threshold(Variable):
    value_type = float
    entity = TaxUnit
    label = "NYC income tax elimination credit income threshold"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.nysenate.gov/legislation/laws/TAX/1310",
        "https://www.tax.ny.gov/pdf/2025/inc/it270i_2025.pdf#page=1",
    )
    defined_for = "in_nyc"

    def formula(tax_unit, period, parameters):
        # Tax Law § 1310(h)(1)(B); Form IT-270, Part 2, line 2. The
        # threshold depends on filing status and the number of dependents; a
        # tax unit without dependents has no threshold.
        dependents = tax_unit("tax_unit_dependents", period)
        filing_status = tax_unit("filing_status", period)
        filing_statuses = filing_status.possible_values
        p = parameters(
            period
        ).gov.local.ny.nyc.tax.income.credits.income_tax_elimination.income_threshold
        return select(
            [
                filing_status == filing_statuses.SINGLE,
                filing_status == filing_statuses.JOINT,
                filing_status == filing_statuses.HEAD_OF_HOUSEHOLD,
                filing_status == filing_statuses.SURVIVING_SPOUSE,
                filing_status == filing_statuses.SEPARATE,
            ],
            [
                p.single.calc(dependents),
                p.joint.calc(dependents),
                p.head_of_household.calc(dependents),
                p.surviving_spouse.calc(dependents),
                p.separate.calc(dependents),
            ],
        )
