from policyengine_us.model_api import *


class savings_bond_education_exclusion_magi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Modified AGI for the savings bond education exclusion"
    documentation = (
        "Form 8815 line 9 worksheet: gross income less above-the-line "
        "deductions other than the exclusion itself and the student loan "
        "interest deduction. Taxable Social Security benefits are left out "
        "and unemployment compensation is counted in full, because both are "
        "computed from an AGI that includes this exclusion; supply "
        "savings_bond_education_exclusion_magi_override to use an exact "
        "figure. Foreign and possession exclusions are not added back."
    )
    unit = USD
    definition_period = YEAR
    reference = "https://www.irs.gov/pub/irs-pdf/f8815.pdf"

    def formula(tax_unit, period, parameters):
        override = tax_unit("savings_bond_education_exclusion_magi_override", period)
        p = parameters(period).gov.irs
        sources = [
            s
            for s in p.gross_income.sources
            if s not in ("taxable_social_security", "taxable_unemployment_compensation")
        ]
        person = tax_unit.members
        not_dependent = ~person("is_tax_unit_dependent", period)
        gross = 0
        for source in sources + ["unemployment_compensation"]:
            gross += not_dependent * max_(0, add(person, period, [source]))
        excluded = {"us_bonds_for_higher_ed", "student_loan_interest_ald"}
        deductions = [d for d in p.ald.deductions if d not in excluded]
        alds = tax_unit_non_dep_add(
            tax_unit,
            period,
            deductions,
            include_dependents=p.ald.filer_amounts_recorded_on_dependents,
        )
        magi = tax_unit.sum(gross) - alds
        return where(override > 0, override, magi)
