from policyengine_us.model_api import *


class ms_agi(Variable):
    value_type = float
    entity = Person
    label = "Mississippi adjusted gross income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.dor.ms.gov/sites/default/files/tax-forms/individual/80100221.pdf#page=14",
        "https://www.dor.ms.gov/sites/default/files/tax-forms/individual/80105228.pdf",  # Line 66
        # Combined return: one spouse's income in Column A, the other's in B
        "https://www.dor.ms.gov/sites/default/files/tax-forms/individual/80100221.pdf#page=5",
        # Borrowed for dependents' income: parents filing separately report a
        # child's income on the return of the parent with the greater
        # taxable income
        "https://www.law.cornell.edu/uscode/text/26/1#g_5_B",
        "https://www.irs.gov/instructions/i8814",
    )
    defined_for = StateCode.MS

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ms.tax.income
        gross_income = add(person, period, p.income_sources)
        adjustments = person("ms_agi_adjustments", period)
        # A spouse's column can be negative on a joint or combined return;
        # the tax computation combines it with the other column.
        net_income = gross_income - adjustments
        # Each spouse's column holds their own income. The dependents'
        # positive income the model counts here goes on the column of the
        # spouse with the greater income (a modelling convention; see the
        # helper).
        is_dependent = person("is_tax_unit_dependent", period)
        return move_dependent_amounts_to_filer(
            person, period, where(is_dependent, max_(net_income, 0), net_income)
        )
