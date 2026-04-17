from policyengine_us.model_api import *


class mo_st_louis_earnings_tax_before_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "St. Louis earnings tax before credit"
    documentation = (
        "St. Louis earnings tax before credits for taxes paid to another "
        "state or political subdivision."
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
        return tax_unit.sum(taxable_earnings * p.rate)
