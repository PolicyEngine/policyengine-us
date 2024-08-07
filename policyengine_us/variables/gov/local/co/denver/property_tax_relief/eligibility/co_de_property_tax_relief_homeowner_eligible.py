from policyengine_us.model_api import *


class co_de_property_tax_relief_homeowner_eligible(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Eligible for the homeowner Denver Property Tax Relief"
    definition_period = YEAR
    reference = "https://denvergov.org/files/content/public/v/37/government/agencies-departments-offices/agencies-departments-offices-directory/denver-human-services/be-supported/additional-assistance/property-tax-relief/denver-property-tax-relief-program-year-2021-rules.pdf"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.local.co.denver.property_tax_relief
        has_property_taxes = add(spm_unit, period, ["real_estate_taxes"]) > 0
        has_elderly_or_disabled = spm_unit("has_usda_elderly_disabled", period)
        count_dependents = add(spm_unit, period, ["tax_unit_dependents"])
        has_dependent = count_dependents > 0
        homeowner_requirments = (
            has_elderly_or_disabled | has_dependent
        ) & has_property_taxes

        income = spm_unit("spm_unit_net_income", period)
        size = spm_unit("spm_unit_size", period)
        homeowner_income_limit = p.ami.ami.calc(size) * p.ami.rate.homeowner
        homeowner_income_eligible = income <= homeowner_income_limit

        return homeowner_requirments & homeowner_income_eligible
