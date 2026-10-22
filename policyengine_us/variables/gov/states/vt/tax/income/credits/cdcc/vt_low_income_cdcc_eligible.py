from policyengine_us.model_api import *


class vt_low_income_cdcc_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Vermont low-income child care and dependent care credit"
    definition_period = YEAR
    reference = (
        "https://tax.vermont.gov/sites/tax/files/documents/IN-112-2021.pdf#page=2",
        "https://law.justia.com/codes/vermont/2021/title-32/chapter-151/section-5828c/",
        # 2022 Act 138 section 3 reproduces the pre-2022 text it amended.
        "https://legislature.vermont.gov/Documents/2022/Docs/ACTS/ACT138/ACT138%20As%20Enacted.pdf#page=3",
    )
    defined_for = StateCode.VT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.vt.tax.income.credits.cdcc.low_income
        filing_status = tax_unit("filing_status", period)
        federal_agi_threshold = p.income_threshold[filing_status]
        federal_agi = tax_unit("adjusted_gross_income", period)
        # 32 V.S.A. 5828c (as in effect through 2021) requires federal adjusted
        # gross income "less than $30,000.00 (or $40,000.00 for married,
        # filing jointly)"; the 2021 Schedule IN-112 says "$30,000 (or $40,000
        # for Married Filing Jointly) or less". The model follows the statute.
        return federal_agi < federal_agi_threshold
