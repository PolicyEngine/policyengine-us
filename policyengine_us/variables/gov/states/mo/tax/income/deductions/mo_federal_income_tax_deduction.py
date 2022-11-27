from policyengine_us.model_api import *


class mo_federal_income_tax_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "MO Federal income tax deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.mo.gov/forms/MO-1040%20Instructions_2021.pdf#page=7",
        "https://revisor.mo.gov/main/OneSection.aspx?section=143.171&bid=49937&hl=federal+income+tax+deduction%u2044",
    )
    defined_for = StateCode.MO

    def formula(tax_unit, period, parameters):

        # compute federal income tax ignoring COVID-19 rebates and federal EITC
        # (see second reference above for the legislative language)
        p = parameters(period).gov.states.mo.tax.income.deductions
        ignored_credits = p.federal_income_tax_deduction_ignored_credits
        ignored_credits_total = add(tax_unit, period, ignored_credits)
        fitax = tax_unit("income_tax", period)
        fitax_ignoring_credits = max_(0, fitax + ignored_credits_total)

        # compute deduction rate based on MO AGI
        fitax_deduction_rates = p.federal_income_tax_deduction_rates
        mo_agi = add(tax_unit, period, ["mo_adjusted_gross_income"])
        rate = fitax_deduction_rates.calc(mo_agi)

        # compute uncapped deduction amount
        fitax_deduction_amt = fitax_ignoring_credits * rate

        # compute deduction cap based on filing status
        fstatus = tax_unit("filing_status", period)
        fitax_deduction_cap = p.federal_income_tax_deduction_caps[fstatus]

        return min_(
            fitax_deduction_amt,
            fitax_deduction_cap,
        )
