from policyengine_us.model_api import *


class mo_income_tax_before_credits(Variable):
    value_type = float
    entity = Person
    label = "Missouri income tax before credits"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.mo.gov/forms/MO-1040%20Print%20Only_2021.pdf",
        "https://www.revisor.mo.gov/main/OneChapter.aspx?chapter=143",
        "https://dor.mo.gov/forms/MO-1040%20Instructions_2023.pdf#page=26",
        "https://dor.mo.gov/forms/MO-1040%20Instructions_2025.pdf#page=21",
    )
    defined_for = StateCode.MO

    def formula(person, period, parameters):
        taxable_income = person("mo_taxable_income", period)
        p = parameters(period).gov.states.mo.tax.income
        # The tax rate chart gives the tax as a base amount plus the bracket's
        # rate on the excess over the bracket's threshold, for income "over"
        # that threshold "but not over" the next.
        thresholds = np.array(p.rates.thresholds)
        rates = np.array(p.rates.rates)
        # The top threshold can be infinite; no income reaches its base.
        widths = np.nan_to_num(np.diff(thresholds), posinf=0)
        full_bracket_tax = rates[:-1] * widths
        # Each base adds the lower brackets' taxes, which the chart rounds to
        # whole dollars one bracket at a time.
        full_bracket_tax = where(
            p.tax_chart.whole_dollar_base_amounts,
            np.floor(full_bracket_tax + 0.5),
            full_bracket_tax,
        )
        base_amounts = np.concatenate(([0], np.cumsum(full_bracket_tax)))
        bracket = max_(np.searchsorted(thresholds, taxable_income, side="left") - 1, 0)
        excess = max_(taxable_income - thresholds[bracket], 0)
        tax = base_amounts[bracket] + rates[bracket] * excess
        # Fifty cents rounds up, as the return instructions require.
        tax = where(p.tax_chart.round_tax, np.floor(tax + 0.5), tax)
        exempt = person("mo_income_tax_exempt", period)
        return where(exempt, 0, tax)
