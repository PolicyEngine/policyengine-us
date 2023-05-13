from policyengine_us.model_api import *


class oh_non_public_school_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = (
        "Ohio Nonchartered, Nonpublic, School Tuition Credit AGI Credit Rates"
    )
    unit = USD
    definition_period = YEAR
    reference = "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=21"
    defined_for = StateCode.OH

    def formula(tax_unit, period, parameters):
        rates = parameters(
            period
        ).gov.states.oh.tax.income.credits.non_public_tuition.agi_credit_amount

        agi = tax_unit("oh_agi", period)
        person = tax_unit.members
        tuitions = sum(person("non_public_school_tuition", period))
        eligible = tuitions > 0
        return rates.calc(agi) * eligible
