from openfisca_us.model_api import *


class capital_gains_excluded_from_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Capital gains excluded from taxable income"
    unit = USD
    documentation = "This is subtracted from taxable income before applying the ordinary tax rates. Capital gains tax is calculated separately."
    definition_period = YEAR
    reference = dict(
        title="26 U.S. Code § 1(h)(1)(A)",
        href="https://www.law.cornell.edu/uscode/text/26/1#h_1_A",
    )

    def formula(tax_unit, period, parameters):
        pass
