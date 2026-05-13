from policyengine_us.model_api import *


def _mortgage_balance_cap(
    origination_year, pre_tcja_cap, post_tcja_cap, pre_tcja_origination_year
):
    # An origination year of 0 means no mortgage; treat as post-TCJA so the
    # lower cap applies (harmless because the balance will also be 0).
    return where(
        (origination_year > 0) & (origination_year <= pre_tcja_origination_year),
        pre_tcja_cap,
        post_tcja_cap,
    )


def _limited_mortgage_balance(first_balance, second_balance, first_cap, second_cap):
    # Under §163(h)(3)(F), pre-TCJA debt keeps the $1M cap and post-TCJA debt
    # gets max(0, $750K − pre_TCJA_debt).  This is equivalent to computing the
    # combined deductible balance as:
    #   min(larger_cap, max(larger_balance, smaller_cap))
    # where "larger/smaller" refer to the balance sizes (not vintages).
    first_is_smaller = first_balance < second_balance
    smaller_cap = where(first_is_smaller, first_cap, second_cap)
    larger_cap = where(first_is_smaller, second_cap, first_cap)
    larger_balance = max_(first_balance, second_balance)
    return min_(larger_cap, max_(larger_balance, smaller_cap))


class first_home_mortgage_balance(Variable):
    value_type = float
    entity = TaxUnit
    label = "First home mortgage balance"
    unit = USD
    definition_period = YEAR
    default_value = 0
    documentation = (
        "Outstanding balance on the first home acquisition mortgage used to "
        "calculate the federal mortgage interest deduction."
    )


class second_home_mortgage_balance(Variable):
    value_type = float
    entity = TaxUnit
    label = "Second home mortgage balance"
    unit = USD
    definition_period = YEAR
    default_value = 0
    documentation = (
        "Outstanding balance on the second home acquisition mortgage used to "
        "calculate the federal mortgage interest deduction."
    )


class first_home_mortgage_interest(Variable):
    value_type = float
    entity = TaxUnit
    label = "First home mortgage interest"
    unit = USD
    definition_period = YEAR
    default_value = 0
    documentation = (
        "Interest paid on the first home acquisition mortgage used to "
        "calculate the federal mortgage interest deduction."
    )


class second_home_mortgage_interest(Variable):
    value_type = float
    entity = TaxUnit
    label = "Second home mortgage interest"
    unit = USD
    definition_period = YEAR
    default_value = 0
    documentation = (
        "Interest paid on the second home acquisition mortgage used to "
        "calculate the federal mortgage interest deduction."
    )


class first_home_mortgage_origination_year(Variable):
    value_type = int
    entity = TaxUnit
    label = "First home mortgage origination year"
    definition_period = YEAR
    default_value = 0
    documentation = "Calendar year when the first home acquisition mortgage originated."


class second_home_mortgage_origination_year(Variable):
    value_type = int
    entity = TaxUnit
    label = "Second home mortgage origination year"
    definition_period = YEAR
    default_value = 0
    documentation = (
        "Calendar year when the second home acquisition mortgage originated."
    )


class home_mortgage_interest_tax_unit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax unit home mortgage interest"
    unit = USD
    definition_period = YEAR
    adds = ["first_home_mortgage_interest", "second_home_mortgage_interest"]


class deductible_mortgage_interest_tax_unit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax unit deductible mortgage interest"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Federal deductible mortgage interest after applying the statutory "
        "acquisition-debt caps to up to two mortgages."
    )
    reference = "https://www.law.cornell.edu/uscode/text/26/163"

    def formula(tax_unit, period, parameters):
        first_balance = tax_unit("first_home_mortgage_balance", period)
        second_balance = tax_unit("second_home_mortgage_balance", period)
        first_interest = tax_unit("first_home_mortgage_interest", period)
        second_interest = tax_unit("second_home_mortgage_interest", period)
        first_year = tax_unit("first_home_mortgage_origination_year", period)
        second_year = tax_unit("second_home_mortgage_origination_year", period)
        total_balance = first_balance + second_balance
        total_interest = first_interest + second_interest

        filing_status = tax_unit("filing_status", period)
        p = parameters(period).gov.irs.deductions.itemized.interest.mortgage
        pre_tcja_cap = p.pre_tcja_cap[filing_status]
        post_tcja_cap = p.cap[filing_status]
        pre_tcja_origination_year = p.pre_tcja_origination_year

        first_cap = _mortgage_balance_cap(
            first_year,
            pre_tcja_cap,
            post_tcja_cap,
            pre_tcja_origination_year,
        )
        second_cap = _mortgage_balance_cap(
            second_year,
            pre_tcja_cap,
            post_tcja_cap,
            pre_tcja_origination_year,
        )
        limited_balance = _limited_mortgage_balance(
            first_balance, second_balance, first_cap, second_cap
        )

        deductible_share = np.zeros_like(total_balance)
        mask = total_balance > 0
        deductible_share[mask] = np.minimum(
            1, limited_balance[mask] / total_balance[mask]
        )
        return total_interest * deductible_share


class non_deductible_mortgage_interest_tax_unit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax unit non-deductible mortgage interest"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Home mortgage interest that is not deductible federally because it "
        "exceeds the acquisition-debt caps."
    )

    def formula(tax_unit, period, parameters):
        total_interest = tax_unit("home_mortgage_interest_tax_unit", period)
        deductible_interest = tax_unit("deductible_mortgage_interest_tax_unit", period)
        return max_(0, total_interest - deductible_interest)
