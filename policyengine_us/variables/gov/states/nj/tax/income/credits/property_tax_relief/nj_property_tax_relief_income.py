from policyengine_us.model_api import *


class nj_property_tax_relief_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey property tax relief application income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.nj.gov/treasury/taxation/relief.shtml#PAS1IncomeCalculation",
        "https://www.nj.gov/treasury/taxation/pdf/25-pas1in.pdf#page=9",
    )
    defined_for = StateCode.NJ

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.nj.tax.income.credits.property_tax_relief.income

        person = tax_unit.members
        nj_gross_income = add(tax_unit, period, ["nj_gross_income"])
        additional_sources = add(tax_unit, period, p.additional_sources)

        age = person("age", period)
        full_retirement_age = (
            person("ss_full_retirement_age_months", period) / MONTHS_IN_YEAR
        )
        total_disability_payments = person("total_disability_payments", period)
        disability_pension_before_retirement_age = tax_unit.sum(
            (age < full_retirement_age) * total_disability_payments
        )

        return (
            nj_gross_income
            + additional_sources
            + disability_pension_before_retirement_age
        )
