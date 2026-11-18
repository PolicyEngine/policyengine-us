from policyengine_us.model_api import *


class ms_agi(Variable):
    value_type = float
    entity = Person
    label = "Mississippi adjusted gross income"
    documentation = (
        "Mississippi adjusted gross income in the head's and spouse's columns "
        "of the return. A tax unit dependent's income belongs on the "
        "dependent's own Mississippi return, so a dependent's amount is zero."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        # PDF pages 5, 14: a combined return puts one spouse's income in
        # Column A and the other's in Column B (p. 5), and line 66,
        # Mississippi adjusted gross income (p. 14)
        "https://www.dor.ms.gov/sites/default/files/tax-forms/individual/80100221.pdf#page=5",
        "https://www.dor.ms.gov/sites/default/files/tax-forms/individual/80105228.pdf",  # Line 66
        # 35 Miss. Admin. Code Pt. III, 10.01.104: a minor is taxable on their
        # own income and files their own return, with their own deductions
        # and exemptions.
        "https://www.law.cornell.edu/regulations/mississippi/35-Miss-Code-R-SS-3-10-01-104",
        # Filing requirements: minor resident taxpayers file their own return
        "https://www.dor.ms.gov/sites/default/files/tax-forms/individual/80100241.pdf#page=4",
    )
    defined_for = StateCode.MS

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ms.tax.income
        gross_income = add(person, period, p.income_sources)
        adjustments = person("ms_agi_adjustments", period)
        # A spouse's column can be negative on a joint or combined return;
        # the tax computation combines it with the other column.
        net_income = gross_income - adjustments
        # Each spouse's column holds their own income. A dependent's income
        # goes on the dependent's own return, not on the filer's.
        is_dependent = person("is_tax_unit_dependent", period)
        return where(is_dependent, 0, net_income)
