from policyengine_us.model_api import *


class ct_property_tax_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Connecticut Property Tax Credit"
    definition_period = YEAR
    defined_for = StateCode.CT
    reference = (
        # (b)(2)
        "https://www.cga.ct.gov/current/pub/chap_229.htm#sec_12-704c",
        "https://www.law.cornell.edu/uscode/text/26/152#b_1",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ct.tax.income.credits.property_tax
        age_eligible = tax_unit("greater_age_head_spouse", period) >= p.age_threshold
        # Through 2021, a filer under the age threshold qualifies only by
        # "validly claiming one or more dependents". A return on which the
        # filer (or, if joint, either spouse) can be claimed as a dependent
        # has no dependents (IRC 152(b)(1)). From 2022 the age threshold is 0,
        # so every filer is age eligible.
        filer_is_dependent = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
        dependents_present = (tax_unit("tax_unit_dependents", period) > 0) & ~(
            filer_is_dependent
        )

        return dependents_present | age_eligible
