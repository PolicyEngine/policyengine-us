from policyengine_us.model_api import *


class denver_property_tax_relief(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Denver Property Tax Relief"
    definition_period = YEAR
    reference = "https://denvergov.org/files/content/public/v/37/government/agencies-departments-offices/agencies-departments-offices-directory/denver-human-services/be-supported/additional-assistance/property-tax-relief/denver-property-tax-relief-program-year-2021-rules.pdf"

    def formula(spm_unit, period, parameters):
        # homeowner
        ## has elderly or has disabled or has dependent AND has paid property taxes AND < income limit
        # renter
        ## has elderly or has disabled AND < income limit
        p = parameters(period).gov.local.co.denver.property_tax_relief
        has_rent = add(spm_unit, period, ["rent"]) > 0
        has_property_taxes = add(spm_unit, period, ["real_estate_taxes"]) > 0
        has_elderly_or_disabled = spm_unit("has_usda_elderly_disabled", period)
        spm_unit_count_dependent = add(
            spm_unit, period, ["tax_unit_dependents"]
        )
        spm_unit_has_dependent = spm_unit_count_dependent > 0
        homeowner_requirments = (
            has_elderly_or_disabled | spm_unit_has_dependent
        ) & has_property_taxes
        renter_requirements = has_elderly_or_disabled & has_rent

        # income means earnings/wages, social security income, other income
        income = spm_unit("spm_unit_net_income", period)
        size = spm_unit("spm_unit_size", period)
        homeowner_income_limit = p.ami.ami.calc(size) * p.ami.rate.homeowner
        homeowner_income_eligible = income <= homeowner_income_limit

        renter_income_limit = p.ami.ami.calc(size) * p.ami.rate.renter.calc(
            size
        )
        renter_income_eligible = income <= renter_income_limit

        return select(
            [
                homeowner_requirments & homeowner_income_eligible,
                renter_requirements & renter_income_eligible,
            ],
            [p.maximum_amount.homeowner, p.maximum_amount.renter],
            default=0,
        )
