from policyengine_us.model_api import *


class tx_dart_reduced_fare_eligible(Variable):
    value_type = bool
    entity = Person
    label = (
        "Eligible for Dallas Area Rapid Transit (DART) Reduced Fare program"
    )
    definition_period = YEAR
    defined_for = StateCode.TX
    reference = (
        "https://www.dart.org/fare/general-fares-and-overview/reduced-fares"
    )

    def formula(person, period, parameters):
        # Eligible due to age
        age_eligible = person("tx_dart_reduced_fare_age_eligible", period)
        # Disability
        is_disabled = person("is_disabled", period)
        # Veteran
        veteran_eligible = person("is_veteran", period)
        # Student (high school, college, or trade school)
        student_eligible = person("is_full_time_student", period)
        # Enrolled in applicable programs (Discount GoPass)
        # Note: DART has two separate programs that both offer 50% discounts:
        # 1. Reduced Fare program (for age/disability/veteran/student)
        # 2. Discount GoPass program (for assistance program recipients)
        # We combine them here since they provide identical benefits
        enrolled_eligible = person(
            "tx_dart_reduced_fare_program_eligible", period
        )

        return (
            age_eligible
            | is_disabled
            | veteran_eligible
            | student_eligible
            | enrolled_eligible
        )
