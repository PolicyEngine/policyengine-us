from policyengine_us.model_api import *


class SSIFederalLivingArrangement(Enum):
    OWN_HOUSEHOLD = "Own household"
    ANOTHER_PERSONS_HOUSEHOLD = "Another person's household"
    CHILD_IN_PARENTAL_HOUSEHOLD = "Child in parental household"
    MEDICAL_TREATMENT_FACILITY = "Medical treatment facility"


class ssi_federal_living_arrangement(Variable):
    value_type = Enum
    entity = Person
    label = "SSI federal living arrangement"
    definition_period = YEAR
    possible_values = SSIFederalLivingArrangement
    default_value = SSIFederalLivingArrangement.OWN_HOUSEHOLD
    reference = (
        "https://www.law.cornell.edu/cfr/text/20/416.1132",
        "https://www.law.cornell.edu/cfr/text/20/416.1131",
        "https://www.law.cornell.edu/cfr/text/20/416.1165",
        "https://www.law.cornell.edu/cfr/text/20/416.414",
    )

    def formula(person, period, parameters):
        # Classification priority: medical facility first, then child
        # in parental household, then another person's household,
        # then own household as residual.

        # 42 USC § 1382(e)(1)(A), 20 CFR § 416.414:
        # Medical treatment facility with Medicaid paying >50%
        is_medical_facility = person(
            "ssi_lives_in_medical_treatment_facility", period
        ) & person("ssi_medicaid_pays_majority_of_care", period)

        # 20 CFR § 416.1165: Child under 18 with ineligible parent
        # in the tax unit. Under-22 students are excluded because
        # is_ssi_ineligible_parent keys off is_child (age < 18);
        # extending to under-22 students requires updating the
        # deeming framework.
        has_ineligible_parent = (
            person.tax_unit.sum(
                person.tax_unit.members("is_ssi_ineligible_parent", period)
            )
            > 0
        )
        is_child_in_parental = (
            ~is_medical_facility & person("is_child", period) & has_ineligible_parent
        )

        # 20 CFR § 416.1131–1133: In another person's household
        # AND receives shelter AND others pay all meals (the
        # one-third reduction gateway conditions)
        in_another_household = person("ssi_lives_in_another_persons_household", period)
        receives_shelter = person(
            "ssi_receives_shelter_from_others_in_household", period
        )
        all_meals_paid = person("ssi_others_pay_all_meals", period)
        is_another_household = (
            ~is_medical_facility
            & ~is_child_in_parental
            & in_another_household
            & receives_shelter
            & all_meals_paid
        )

        # 20 CFR § 416.1132(c): Own household (residual)
        return select(
            [is_medical_facility, is_child_in_parental, is_another_household],
            [
                SSIFederalLivingArrangement.MEDICAL_TREATMENT_FACILITY,
                SSIFederalLivingArrangement.CHILD_IN_PARENTAL_HOUSEHOLD,
                SSIFederalLivingArrangement.ANOTHER_PERSONS_HOUSEHOLD,
            ],
            default=SSIFederalLivingArrangement.OWN_HOUSEHOLD,
        )
