from policyengine_us.model_api import *


class pell_grant_simplified(Variable):
    value_type = bool
    entity = Person
    label = "Use Pell Grant simplified formula"
    definition_period = YEAR

    def formula(person, period, parameters):
        tax_unit = person.tax_unit
        head_income = tax_unit("pell_grant_head_income", period)
        max_income = parameters(period).gov.ed.pell_grant.efc.simplified.max_income
        income_eligible = head_income < max_income
        medicaid = add(tax_unit, period, ["medicaid"])
        ssi = add(tax_unit, period, ["ssi"])
        snap = person.spm_unit("snap", period)
        free_lunch = person.spm_unit("free_school_meals", period)
        reduced_lunch = person.spm_unit("reduced_price_school_meals", period)
        tanf = person.spm_unit("tanf", period)
        wic = add(tax_unit, period, ["wic"])
        total_benefits = medicaid + ssi + snap + free_lunch + reduced_lunch + tanf + wic
        has_benefits = total_benefits > 0
        return income_eligible & has_benefits
