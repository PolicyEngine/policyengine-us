from policyengine_us.model_api import *


class early_distribution_allowed_exceptions(Variable):
    value_type = float
    entity = Person
    label = "Early distributions from plans and IRAs excepted from the additional tax"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/72#t_2",
        "https://www.irs.gov/instructions/i5329",
    )

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.irs.retirement_distributions.early_distribution_tax.exception_caps
        homebuyer = min_(
            person("early_distribution_first_time_homebuyer", period),
            max_(
                0,
                p.first_time_homebuyer
                - person("early_distribution_first_time_homebuyer_prior_use", period),
            ),
        )
        birth = min_(
            person("early_distribution_birth_or_adoption", period),
            p.birth_or_adoption
            * person("early_distribution_birth_or_adoption_children", period),
        )
        emergency = min_(
            person("early_distribution_emergency_personal_expense", period),
            p.emergency_personal_expense,
        )
        abuse = min_(
            person("early_distribution_domestic_abuse_victim", period),
            p.domestic_abuse_victim,
        )
        disaster = min_(
            person("early_distribution_qualified_disaster", period),
            p.qualified_disaster
            * person("early_distribution_qualified_disasters", period),
        )
        # The medical exception is limited to the tax unit's medical expenses
        # above the AGI floor (the section 213 amount, itemized or not),
        # shared among members in proportion to their claims.
        medical_claim = max_(person("early_distribution_medical_expense", period), 0)
        unit_claim = person.tax_unit.sum(medical_claim)
        unit_cap = person.tax_unit("early_distribution_medical_expense_cap", period)
        share = np.divide(
            medical_claim,
            unit_claim,
            out=np.zeros_like(medical_claim),
            where=unit_claim > 0,
        )
        medical = min_(medical_claim, share * unit_cap)
        excepted = (
            max_(person("early_distribution_exceptions_uncapped", period), 0)
            + homebuyer
            + birth
            + emergency
            + abuse
            + disaster
            + medical
        )
        return min_(
            excepted,
            max_(person("early_distributions_from_retirement_plans", period), 0),
        )
