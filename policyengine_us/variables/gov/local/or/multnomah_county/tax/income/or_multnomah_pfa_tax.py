from policyengine_us.model_api import *


class or_multnomah_pfa_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Multnomah County Preschool for All Personal Income Tax"
    unit = USD
    definition_period = YEAR
    defined_for = "in_multnomah_county_or"
    reference = (
        "https://multco.us/file/preschool_for_all_personal_income_tax_code/download",
        "https://multco.us/info/multnomah-county-preschool-all-personal-income-tax",
    )

    def formula(tax_unit, period, parameters):
        # Per MCC 11.510, taxable income is Oregon taxable income
        taxable_income = tax_unit("or_taxable_income", period)
        filing_status = tax_unit("filing_status", period)
        statuses = filing_status.possible_values

        # Per MCC 11.512(C): Joint thresholds apply to joint, HOH, and surviving spouse
        # Single thresholds apply to single and married filing separately
        p = (
            parameters(period)
            .gov.local["or"]
            .multnomah_county.tax.income.pfa.rates
        )

        return select(
            [
                filing_status == statuses.SINGLE,
                filing_status == statuses.SEPARATE,
                filing_status == statuses.JOINT,
                filing_status == statuses.HEAD_OF_HOUSEHOLD,
                filing_status == statuses.SURVIVING_SPOUSE,
            ],
            [
                p.single.calc(taxable_income),
                p.separate.calc(taxable_income),
                p.joint.calc(taxable_income),
                p.head_of_household.calc(taxable_income),
                p.surviving_spouse.calc(taxable_income),
            ],
        )
