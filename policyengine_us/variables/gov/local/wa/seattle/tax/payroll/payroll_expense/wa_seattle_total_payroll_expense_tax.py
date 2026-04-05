from policyengine_us.model_api import *


class wa_seattle_total_payroll_expense_tax(Variable):
    value_type = float
    entity = Person
    label = "Total Seattle payroll expense tax"
    documentation = (
        "Employer-side Seattle payroll expense tax liability from aggregate "
        "prior-year payroll, current-year payroll, and taxable payroll-band "
        "inputs."
    )
    definition_period = YEAR
    unit = USD
    reference = (
        "https://www.seattle.gov/city-finance/business-taxes-and-licenses/"
        "seattle-taxes/payroll-expense-tax"
    )

    def formula(person, period, parameters):
        state_code = person.household("state_code", period)
        p = parameters(period).gov.local.wa.seattle.tax.payroll.payroll_expense
        prior_year_total = person(
            "employer_total_wa_seattle_payroll_expense_prior_year_total", period
        )
        current_year_total = person(
            "employer_total_wa_seattle_payroll_expense_current_year_total", period
        )
        lower_band_taxable_payroll = person(
            "employer_total_wa_seattle_payroll_expense_lower_band_taxable_payroll",
            period,
        )
        upper_band_taxable_payroll = person(
            "employer_total_wa_seattle_payroll_expense_upper_band_taxable_payroll",
            period,
        )
        lower_band_rate = p.rates.lower_band.calc(current_year_total)
        upper_band_rate = p.rates.upper_band.calc(current_year_total)
        subject = (prior_year_total >= p.prior_year_total_payroll_expense_threshold) & (
            state_code == StateCode.WA
        )

        return where(
            subject,
            lower_band_rate * lower_band_taxable_payroll
            + upper_band_rate * upper_band_taxable_payroll,
            0,
        )
