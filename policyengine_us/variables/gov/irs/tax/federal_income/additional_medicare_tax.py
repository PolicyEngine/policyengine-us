from policyengine_us.model_api import *


class additional_medicare_tax(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Additional Medicare Tax"
    unit = USD
    documentation = (
        "Additional Medicare Tax from Form 8959 (included in payrolltax), on "
        "the Medicare wages and self-employment income of the head and, on a "
        "joint return, the spouse. A tax unit dependent's wages are reported "
        "on the dependent's own Form W-2 and own return, so they are left out."
    )
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/3101#b_2",
        "https://www.law.cornell.edu/uscode/text/26/1401#b_2",
        "https://www.irs.gov/pub/irs-prior/i8959--2024.pdf#page=3",
    )

    def formula(tax_unit, period, parameters):
        amc = parameters(period).gov.irs.payroll.medicare.additional
        # Wage and self-employment income are taxed the same.
        ELEMENTS = ["payroll_tax_gross_wages", "taxable_self_employment_income"]
        wages_plus_se = tax_unit_non_dep_add(tax_unit, period, ELEMENTS)
        exclusion = amc.exclusion[tax_unit("filing_status", period)]
        base = max_(0, wages_plus_se - exclusion)
        return amc.rate * base
