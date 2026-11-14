from policyengine_us.model_api import *


class mo_st_louis_earnings_tax_person(Variable):
    value_type = float
    entity = Person
    label = "St. Louis earnings tax for each person"
    documentation = (
        "St. Louis earnings tax on the person's own taxable earnings, after "
        "the person's optional credits supplied as inputs."
    )
    definition_period = YEAR
    unit = USD
    reference = (
        "https://www.stlouis-mo.gov/government/departments/collector/"
        "earnings-tax/file-earnings-tax.cfm"
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.local.mo.st_louis.tax.income
        taxable_earnings = person("mo_st_louis_earnings_tax_taxable_earnings", period)
        credits = person("mo_st_louis_earnings_tax_credit", period)
        return max_(0, taxable_earnings * p.rate - credits)
