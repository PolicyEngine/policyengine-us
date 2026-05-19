from policyengine_us.tools.tax_unit_construction import (
    CPSRelationshipCode,
    dependent_gross_income_limit,
    qualifying_child_age_test,
    qualifying_relative_income_test,
    reference_relationship_allows_qualifying_child,
    reference_relationship_allows_qualifying_relative,
    related_to_head_or_spouse,
)


def test_qualifying_child_age_test_matches_irs_thresholds():
    assert qualifying_child_age_test(age=18, is_full_time_student=False)
    assert not qualifying_child_age_test(age=19, is_full_time_student=False)
    assert qualifying_child_age_test(age=23, is_full_time_student=True)
    assert not qualifying_child_age_test(age=24, is_full_time_student=True)
    assert qualifying_child_age_test(
        age=40,
        is_full_time_student=False,
        is_permanently_disabled=True,
    )


def test_reference_relationship_predicates_match_cps_codes():
    assert reference_relationship_allows_qualifying_child(CPSRelationshipCode.OWN_CHILD)
    assert reference_relationship_allows_qualifying_child(
        CPSRelationshipCode.GRANDCHILD
    )
    assert not reference_relationship_allows_qualifying_child(
        CPSRelationshipCode.PARENT
    )

    assert reference_relationship_allows_qualifying_relative(CPSRelationshipCode.PARENT)
    assert reference_relationship_allows_qualifying_relative(
        CPSRelationshipCode.SIBLING
    )
    assert not reference_relationship_allows_qualifying_relative(
        CPSRelationshipCode.PARTNER_OR_ROOMMATE
    )

    assert related_to_head_or_spouse(CPSRelationshipCode.OTHER_RELATIVE)
    assert not related_to_head_or_spouse(CPSRelationshipCode.PARTNER_OR_ROOMMATE)


def test_dependent_gross_income_limit_reads_parameter_series():
    assert dependent_gross_income_limit(2022) == 4_400
    assert dependent_gross_income_limit(2024) == 5_050
    assert dependent_gross_income_limit(2026) == 5_300


def test_qualifying_relative_income_test_uses_year_specific_limit():
    assert qualifying_relative_income_test(4_000, 2022)
    assert not qualifying_relative_income_test(4_500, 2022)
    assert qualifying_relative_income_test(5_000, 2024)
    assert not qualifying_relative_income_test(5_100, 2024)
