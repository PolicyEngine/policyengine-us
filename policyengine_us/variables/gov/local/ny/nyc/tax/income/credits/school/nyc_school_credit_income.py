from policyengine_us.model_api import *


class nyc_school_credit_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "NYC income used for school tax credit"
    unit = USD
    definition_period = YEAR
    defined_for = "in_nyc"
    adds = ["adjusted_gross_income"]

    # NYC School Tax Credit has its own definition of income.
    # "Income, for purposes of determining your New York City school tax credit, means your recomputed federal adjusted gross income from
    # Form IT-201, line 19a, minus distributions from an individual retirement account and an individual retirement annuity, from Form IT-201,
    # line 9, if they were included in your recomputed federal adjusted gross income."
    # https://www.tax.ny.gov/pdf/2022/printable-pdfs/inc/it201i-2022.pdf#page=26.

    # Recomputed federal AGI is only different from federal AGI if you were required to report any adjustments due to Decoupling from the IRC.
    # If we choose to ignore this possibility for now, then I think School Tax Credit Income = Federal AGI
    # https://www.tax.ny.gov/pdf/current_forms/it/it558i.pdf
