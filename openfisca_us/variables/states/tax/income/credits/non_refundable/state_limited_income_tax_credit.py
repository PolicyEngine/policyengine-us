from openfisca_us.model_api import *


class state_limited_income_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "State limited income tax credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.mass.gov/doc/2021-schedule-nts-l-nrpy-no-tax-status-and-limited-income-credit/download"

    def formula(tax_unit, period, parameters):
        # Line numbers refer to MA's 2021 Schedule NTS-L-NR/PY.
        # Line 10.
        agi = tax_unit("adjusted_gross_income", period)
        exempt = tax_unit("is_state_income_tax_exempt", period)
        # Lines 10-12: Compute eligibility based on income limit.
        state = tax_unit.household("state_code_str", period)
        filing_status = tax_unit("filing_status", period)
        p = parameters(
            period
        ).states.tax.income.credits.non_refundable.limited_income
        filer_limit = p.income_limit.filer[state][filing_status]
        dep_limit = p.income_limit.dependent[state][filing_status]
        dependents = tax_unit("tax_unit_dependents", period)
        limit = filer_limit + (dep_limit * dependents)
        eligible = agi <= limit
        # Line 13 ("No Tax Status" in MA).
        exempt_limit = tax_unit("state_income_tax_exempt_limit", period)
        # Line 14.
        income_for_credit = agi - exempt_limit
        # Line 15.
        tax_bc = tax_unit("state_income_tax_before_credits", period)
        # Line 16.
        tax_for_credit = p.percent[state] * income_for_credit
        # Line 17.
        return eligible * ~exempt * max_(0, tax_bc - tax_for_credit)
