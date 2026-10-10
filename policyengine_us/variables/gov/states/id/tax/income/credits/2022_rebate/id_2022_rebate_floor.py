from policyengine_us.model_api import *


class id_2022_rebate_floor(Variable):
    value_type = float
    entity = Person
    label = "Idaho 2022 rebate floor"
    definition_period = YEAR
    defined_for = StateCode.ID
    reference = (
        # Idaho Code 63-3024B(3): "seventy-five dollars ($75.00) per taxpayer and
        # each dependent", based on the 2020 return.
        "https://legislature.idaho.gov/statutesrules/idstat/Title63/T63CH30/SECT63-3024B/",
        "https://www.law.cornell.edu/uscode/text/26/152#b_1",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.id.tax.income.credits["2022_rebate"]
        # Each taxpayer counts, even one whom another taxpayer can claim, but a
        # return on which the filer (or, if joint, either spouse) can be
        # claimed has no dependents (IRC 152(b)(1)).
        filer = person("is_tax_unit_head_or_spouse", period)
        filer_is_dependent = person.tax_unit(
            "head_or_spouse_is_dependent_elsewhere", period
        )
        return p.floor * (filer | ~filer_is_dependent)
