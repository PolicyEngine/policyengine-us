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
        total_subtractions = add(person, period, p.deductions)
        # A tax unit dependent's U.S. government interest is on the dependent's
        # own return and never in the filer's federal AGI, so it is not
        # subtracted here, where each person's amounts are summed into the
        # filer's.
        if "us_govt_interest_person" in p.deductions:
            dependent = person("is_tax_unit_dependent", period)
            total_subtractions = total_subtractions - dependent * person(
                "us_govt_interest_person", period
            )
        return total_subtractions
