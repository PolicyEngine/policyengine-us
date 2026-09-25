from policyengine_us.model_api import *


class ar_medical_expense_deduction_floor(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arkansas medical expense deduction floor"
    unit = "/1"
    definition_period = YEAR
    reference = (
        "https://www.arkleg.state.ar.us/Acts/FTPDocument?path=%2FACTS%2F2025R%2FPublic%2F&file=614.pdf&ddBienniumSession=2025%2F2025R#page=2",
        "https://www.dfa.arkansas.gov/wp-content/uploads/LongBookwTaxTables_2016.pdf#page=38",
    )
    defined_for = StateCode.AR

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.ar.tax.income.deductions.itemized.medical_expense
        person = tax_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        aged = head_or_spouse & (person("age", period) >= p.senior.age_threshold)
        # "You or your spouse" (Form AR3 Line 3B) includes a spouse who files a
        # separate return in another tax unit. Reach that spouse through the
        # marital unit only when it holds exactly the couple: without explicit
        # marital units, everyone shares one default unit.
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        couple = person.marital_unit.nb_persons() == 2
        spouse_aged = couple & person.marital_unit.any(aged)
        senior = tax_unit.any(aged) | (
            separate & tax_unit.any(head_or_spouse & spouse_aged)
        )
        return where(senior, p.senior.income_floor, p.income_floor)
