from policyengine_us.model_api import *


class mo_st_louis_earnings_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "St. Louis earnings tax"
    documentation = (
        "Net St. Louis earnings tax after optional credits supplied as inputs."
    )
    definition_period = YEAR
    unit = USD
    reference = (
        "https://www.stlouis-mo.gov/government/departments/collector/"
        "earnings-tax/file-earnings-tax.cfm"
    )

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(period).gov.local.mo.st_louis.tax.income
        taxable_earnings = person("mo_st_louis_earnings_tax_taxable_earnings", period)
        credits = person("mo_st_louis_earnings_tax_credit", period)
        person_tax = taxable_earnings * p.rate
        return tax_unit.sum(max_(0, person_tax - credits))
