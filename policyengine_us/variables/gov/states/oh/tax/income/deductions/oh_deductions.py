from policyengine_us.model_api import *


class oh_deductions(Variable):
    value_type = float
    entity = Person
    label = "Ohio deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.ohio.gov/static/communications/publications/individual_income_tax_ohio.pdf#page=2",
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/it1040-bundle.pdf#page=3",
        "https://cms7files1.revize.com/starkcountyoh/Document_center/Offices/Auditor/Services/Homestead%20Exemption/Ohio_Adj_Gross_Income.pdf",
    )
    defined_for = StateCode.OH

    def formula(person, period, parameters):
        p = parameters(period).gov.states.oh.tax.income.deductions
        # Each person's Ohio AGI is summed into the filer's (oh_agi), so a tax
        # unit dependent gets only the filer's amounts recorded on them, such
        # as medical expenses the filer paid for them. The dependent's own
        # income and expenses belong on their own return.
        return person_non_dep_add(
            person,
            period,
            p.deductions,
            include_dependents=p.filer_amounts_recorded_on_dependents,
        )
