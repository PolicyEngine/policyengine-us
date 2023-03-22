from policyengine_us.model_api import *


class nj_dependents_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey qualified and other dependent children exemption"
    reference = "https://casetext.com/statute/new-jersey-statutes/title-54a-new-jersey-gross-income-tax-act/chapter-54a3-personal-exemptions-and-deductions/section-54a3-1-personal-exemptions-and-deductions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NJ

    def formula(tax_unit, period, parameters):
        # Then get the NJ Exemptions part of the parameter tree.
        p = parameters(period).gov.states.nj.tax.income.exemptions.dependents

        # Total the number of dependents.
        dependents = tax_unit("tax_unit_dependents", period)

        # Get their dependent exemption amount based on their filing status.
        return dependents * p.amount
