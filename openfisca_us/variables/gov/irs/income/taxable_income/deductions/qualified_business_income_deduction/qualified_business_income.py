from openfisca_us.model_api import *


class qualified_business_income(Variable):
    value_type = float
    entity = Person
    label = "Qualified business income"
    documentation = "Income connected with the trade or conduct of a qualified trade or business. A qualified trade or business is any trade or business other than a specified service trade or business, or employment. The list of specified service trades can be found at https://www.law.cornell.edu/uscode/text/26/1202#e_3_A."
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/199A#c"

    def formula(tax_unit, period, parameters):
        components = parameters(
            period
        ).irs.deductions.qbi.max.income_definition
        total_income = add(tax_unit, period, components)
        qualified = tax_unit("business_is_qualified", period)
        return total_income * qualified

    # Note. does not implement https://www.law.cornell.edu/uscode/text/26/199A#d_3, which provides exceptions for where some specified service business income may be
    # treated as qualified business income depending on taxable income.
