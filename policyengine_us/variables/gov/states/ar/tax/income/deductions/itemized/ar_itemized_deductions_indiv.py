from policyengine_us.model_api import *


class ar_itemized_deductions_indiv(Variable):
    value_type = float
    entity = Person
    label = "Arkansas itemized deductions when married couples are filing separately"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.dfa.arkansas.gov/wp-content/uploads/2022_AR3_ItemizedDeduction.pdf",
        "https://www.dfa.arkansas.gov/wp-content/uploads/2021_AR1000F_and_AR1000NR_Instructions.pdf#page=20",
    )
    defined_for = StateCode.AR

    def formula(person, period, parameters):
        # Arkansas does not tie itemization choice to federal choice.
        p = parameters(period).gov.states.ar.tax.income.deductions.itemized.sources
        unit_deds = add(person.tax_unit, period, p.individual)
        # Arkansas freezes IRC 163 as of January 1, 2017, when the premium
        # deduction had expired after 2016 (AR3 interest lines 8-10).
        disallowed_interest = parameters(
            period
        ).gov.states.ar.tax.income.deductions.itemized.disallowed_interest_components
        if disallowed_interest:
            unit_deds = unit_deds - add(person.tax_unit, period, disallowed_interest)
        person_agi = person("ar_agi_indiv", period)
        total_agi = person.tax_unit.sum(person_agi)

        prorate = np.zeros_like(total_agi)
        mask = total_agi > 0
        prorate[mask] = person_agi[mask] / total_agi[mask]

        # Round prorate to the nearest percent and then divide by 100
        prorate = np.round(prorate * 100) / 100

        # Dependents should always return 0 as ar_agi_indiv puts their
        # income on a spouse's column
        return unit_deds * prorate
