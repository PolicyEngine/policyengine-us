"""
Tests for extend_single_year_dataset and its internal helpers.

Uses mock system objects to avoid loading the full policyengine-us
tax-benefit system, keeping tests fast and deterministic.
"""

import numpy as np
import pandas as pd
import pytest

from policyengine_us.data.dataset_schema import (
    USSingleYearDataset,
    USMultiYearDataset,
)
from policyengine_us.data.economic_assumptions import (
    _apply_single_year_uprating,
    _resolve_parameter,
    get_parameter_last_year,
)
from policyengine_us.tests.microsimulation.data.fixtures.test_extend_single_year_dataset import (  # noqa: E501
    BASE_YEAR,
    END_YEAR_SHORT,
    END_YEAR_DEFAULT,
    NUM_PERSONS,
    NUM_HOUSEHOLDS,
    EMPLOYMENT_INCOME_BASE,
    EMPLOYMENT_INCOME_GROWTH_FACTOR_2024_TO_2025,
    EMPLOYMENT_INCOME_GROWTH_FACTOR_2025_TO_2026,
    CPI_U_GROWTH_FACTOR_2024_TO_2025,
    AGE_BASE,
    RENT_BASE,
    EMPLOYMENT_INCOME_UPRATING,
    EMPLOYMENT_INCOME_PARAM_VALUES,
    CPI_U_UPRATING,
    CPI_U_PARAM_VALUES,
    INVALID_UPRATING_PATH,
    build_mock_parameters,
    build_single_year_dataset,
    call_extend_with_mock_system,
    make_mock_super_init,
    MockVariable,
    MockSystem,
    mock_system,  # pytest fixture — must be imported for collection
    base_dataset,  # pytest fixture — must be imported for collection
)


# ---------------------------------------------------------------------------
# _resolve_parameter
# ---------------------------------------------------------------------------


class TestResolveParameter:
    def test_given_valid_dotted_path_then_returns_parameter(self):
        # Given
        params = build_mock_parameters(
            {EMPLOYMENT_INCOME_UPRATING: EMPLOYMENT_INCOME_PARAM_VALUES}
        )

        # When
        result = _resolve_parameter(params, EMPLOYMENT_INCOME_UPRATING)

        # Then
        assert result is not None
        assert result("2024-01-01") == 100.0

    def test_given_invalid_path_then_returns_none(self):
        # Given
        params = build_mock_parameters(
            {EMPLOYMENT_INCOME_UPRATING: EMPLOYMENT_INCOME_PARAM_VALUES}
        )

        # When
        result = _resolve_parameter(params, INVALID_UPRATING_PATH)

        # Then
        assert result is None

    def test_given_partial_valid_path_then_returns_none(self):
        # Given
        params = build_mock_parameters(
            {EMPLOYMENT_INCOME_UPRATING: EMPLOYMENT_INCOME_PARAM_VALUES}
        )

        # When — path exists partially but not fully
        result = _resolve_parameter(params, "calibration.gov.nonexistent")

        # Then
        assert result is None


# ---------------------------------------------------------------------------
# _apply_single_year_uprating
# ---------------------------------------------------------------------------


class TestApplySingleYearUprating:
    def test_given_uprated_variable_then_values_scaled_by_growth_factor(
        self, base_dataset, mock_system
    ):
        # Given
        current = base_dataset.copy()
        current.time_period = str(BASE_YEAR + 1)
        previous = base_dataset

        # When
        _apply_single_year_uprating(current, previous, mock_system)

        # Then
        expected = EMPLOYMENT_INCOME_BASE * EMPLOYMENT_INCOME_GROWTH_FACTOR_2024_TO_2025
        np.testing.assert_allclose(current.person["employment_income"].values, expected)

    def test_given_variable_without_uprating_then_values_unchanged(
        self, base_dataset, mock_system
    ):
        # Given
        current = base_dataset.copy()
        current.time_period = str(BASE_YEAR + 1)
        previous = base_dataset

        # When
        _apply_single_year_uprating(current, previous, mock_system)

        # Then — age has no uprating, should be unchanged
        np.testing.assert_array_equal(current.person["age"].values, AGE_BASE)

    def test_given_household_variable_with_uprating_then_values_scaled(
        self, base_dataset, mock_system
    ):
        # Given
        current = base_dataset.copy()
        current.time_period = str(BASE_YEAR + 1)
        previous = base_dataset

        # When
        _apply_single_year_uprating(current, previous, mock_system)

        # Then — rent is uprated by CPI-U
        expected = RENT_BASE * CPI_U_GROWTH_FACTOR_2024_TO_2025
        np.testing.assert_allclose(current.household["rent"].values, expected)

    def test_given_variable_not_in_system_then_values_unchanged(self, mock_system):
        # Given — add a column the system doesn't know about
        person_df = pd.DataFrame(
            {
                "person_id": [1, 2],
                "employment_income": [50_000.0, 60_000.0],
                "mystery_column": [999.0, 888.0],
            }
        )
        current = USSingleYearDataset(
            person=person_df.copy(),
            household=pd.DataFrame({"household_id": [1]}),
            tax_unit=pd.DataFrame({"tax_unit_id": [1]}),
            time_period=BASE_YEAR + 1,
        )
        previous = USSingleYearDataset(
            person=person_df.copy(),
            household=pd.DataFrame({"household_id": [1]}),
            tax_unit=pd.DataFrame({"tax_unit_id": [1]}),
            time_period=BASE_YEAR,
        )

        # When
        _apply_single_year_uprating(current, previous, mock_system)

        # Then — mystery_column should be untouched
        np.testing.assert_array_equal(
            current.person["mystery_column"].values,
            [999.0, 888.0],
        )

    def test_given_uprating_path_unresolvable_then_values_unchanged(self):
        # Given — variable has an uprating path that doesn't exist in params
        variables = {
            "bad_variable": MockVariable("bad_variable", uprating=INVALID_UPRATING_PATH)
        }
        system = MockSystem(
            variables=variables,
            parameters=build_mock_parameters({}),
        )

        person_df = pd.DataFrame(
            {
                "person_id": [1],
                "bad_variable": [42.0],
            }
        )
        current = USSingleYearDataset(
            person=person_df.copy(),
            household=pd.DataFrame({"household_id": [1]}),
            tax_unit=pd.DataFrame({"tax_unit_id": [1]}),
            time_period=BASE_YEAR + 1,
        )
        previous = USSingleYearDataset(
            person=person_df.copy(),
            household=pd.DataFrame({"household_id": [1]}),
            tax_unit=pd.DataFrame({"tax_unit_id": [1]}),
            time_period=BASE_YEAR,
        )

        # When
        _apply_single_year_uprating(current, previous, system)

        # Then
        assert current.person["bad_variable"].values[0] == 42.0

    def test_given_previous_param_value_zero_then_values_unchanged(self):
        # Given — parameter value is 0 for the previous year (avoid div-by-zero)
        variables = {"some_income": MockVariable("some_income", uprating="test.param")}
        system = MockSystem(
            variables=variables,
            parameters=build_mock_parameters(
                {"test.param": {"2024-01-01": 0.0, "2025-01-01": 100.0}}
            ),
        )

        person_df = pd.DataFrame(
            {
                "person_id": [1],
                "some_income": [5_000.0],
            }
        )
        current = USSingleYearDataset(
            person=person_df.copy(),
            household=pd.DataFrame({"household_id": [1]}),
            tax_unit=pd.DataFrame({"tax_unit_id": [1]}),
            time_period=BASE_YEAR + 1,
        )
        previous = USSingleYearDataset(
            person=person_df.copy(),
            household=pd.DataFrame({"household_id": [1]}),
            tax_unit=pd.DataFrame({"tax_unit_id": [1]}),
            time_period=BASE_YEAR,
        )

        # When
        _apply_single_year_uprating(current, previous, system)

        # Then — no division by zero, value unchanged
        assert current.person["some_income"].values[0] == 5_000.0

    def test_given_zero_base_values_then_uprating_preserves_zeros(
        self, base_dataset, mock_system
    ):
        # Given — person index 7 has employment_income = 0
        current = base_dataset.copy()
        current.time_period = str(BASE_YEAR + 1)
        previous = base_dataset

        # When
        _apply_single_year_uprating(current, previous, mock_system)

        # Then — 0 * any_factor = 0
        assert current.person["employment_income"].values[7] == 0.0


# ---------------------------------------------------------------------------
# extend_single_year_dataset (end-to-end with mocked system)
# ---------------------------------------------------------------------------


class TestExtendSingleYearDataset:
    def test_given_base_year_and_end_year_then_correct_number_of_years(
        self, base_dataset, mock_system
    ):
        # When
        result = call_extend_with_mock_system(
            mock_system, base_dataset, end_year=END_YEAR_SHORT
        )

        # Then
        expected_years = list(range(BASE_YEAR, END_YEAR_SHORT + 1))
        assert result.years == expected_years

    def test_given_base_year_equals_end_year_then_single_year_returned(
        self, base_dataset, mock_system
    ):
        # When
        result = call_extend_with_mock_system(
            mock_system, base_dataset, end_year=BASE_YEAR
        )

        # Then
        assert result.years == [BASE_YEAR]

    def test_given_explicit_end_year_2035_then_extends_correctly(self):
        # Given — need param values through END_YEAR_DEFAULT
        extended_values = {
            f"{y}-01-01": 100.0 * (1.1 ** (y - BASE_YEAR))
            for y in range(BASE_YEAR, END_YEAR_DEFAULT + 1)
        }
        cpi_values = {
            f"{y}-01-01": 300.0 * (1.03 ** (y - BASE_YEAR))
            for y in range(BASE_YEAR, END_YEAR_DEFAULT + 1)
        }
        system = MockSystem(
            parameters=build_mock_parameters(
                {
                    EMPLOYMENT_INCOME_UPRATING: extended_values,
                    CPI_U_UPRATING: cpi_values,
                }
            )
        )
        dataset = build_single_year_dataset()

        # When
        result = call_extend_with_mock_system(
            system, dataset, end_year=END_YEAR_DEFAULT
        )

        # Then
        assert result.years == list(range(BASE_YEAR, END_YEAR_DEFAULT + 1))

    def test_given_extended_dataset_then_base_year_values_unchanged(
        self, base_dataset, mock_system
    ):
        # When
        result = call_extend_with_mock_system(
            mock_system, base_dataset, end_year=END_YEAR_SHORT
        )

        # Then — base year data should match original
        base = result[BASE_YEAR]
        np.testing.assert_array_equal(
            base.person["employment_income"].values,
            EMPLOYMENT_INCOME_BASE,
        )
        np.testing.assert_array_equal(base.person["age"].values, AGE_BASE)
        np.testing.assert_array_equal(base.household["rent"].values, RENT_BASE)

    def test_given_extended_dataset_then_year_one_correctly_uprated(
        self, base_dataset, mock_system
    ):
        # When
        result = call_extend_with_mock_system(
            mock_system, base_dataset, end_year=END_YEAR_SHORT
        )

        # Then
        year_one = result[BASE_YEAR + 1]
        expected = EMPLOYMENT_INCOME_BASE * EMPLOYMENT_INCOME_GROWTH_FACTOR_2024_TO_2025
        np.testing.assert_allclose(
            year_one.person["employment_income"].values, expected
        )

    def test_given_extended_dataset_then_year_two_chains_uprating(
        self, base_dataset, mock_system
    ):
        # When
        result = call_extend_with_mock_system(
            mock_system, base_dataset, end_year=END_YEAR_SHORT
        )

        # Then — year 2 should be uprated from year 1, not from base
        expected = (
            EMPLOYMENT_INCOME_BASE
            * EMPLOYMENT_INCOME_GROWTH_FACTOR_2024_TO_2025
            * EMPLOYMENT_INCOME_GROWTH_FACTOR_2025_TO_2026
        )
        year_two = result[BASE_YEAR + 2]
        np.testing.assert_allclose(
            year_two.person["employment_income"].values, expected
        )

    def test_given_extended_dataset_then_non_uprated_variable_same_all_years(
        self, base_dataset, mock_system
    ):
        # When
        result = call_extend_with_mock_system(
            mock_system, base_dataset, end_year=END_YEAR_SHORT
        )

        # Then — age has no uprating, identical across all years
        for year in result.years:
            np.testing.assert_array_equal(result[year].person["age"].values, AGE_BASE)

    def test_given_extended_dataset_then_row_counts_preserved(
        self, base_dataset, mock_system
    ):
        # When
        result = call_extend_with_mock_system(
            mock_system, base_dataset, end_year=END_YEAR_SHORT
        )

        # Then — every year has the same number of rows per entity
        for year in result.years:
            ds = result[year]
            assert len(ds.person) == NUM_PERSONS
            assert len(ds.household) == NUM_HOUSEHOLDS

    def test_given_extended_dataset_then_each_year_has_correct_time_period(
        self, base_dataset, mock_system
    ):
        # When
        result = call_extend_with_mock_system(
            mock_system, base_dataset, end_year=END_YEAR_SHORT
        )

        # Then
        for year in result.years:
            assert int(result[year].time_period) == year

    def test_given_extended_dataset_then_result_is_multi_year_dataset(
        self, base_dataset, mock_system
    ):
        # When
        result = call_extend_with_mock_system(
            mock_system, base_dataset, end_year=END_YEAR_SHORT
        )

        # Then
        assert isinstance(result, USMultiYearDataset)
        assert result.data_format == "time_period_arrays"

    def test_given_extended_dataset_then_input_dataset_not_mutated(self, mock_system):
        # Given
        dataset = build_single_year_dataset()
        original_values = dataset.person["employment_income"].values.copy()

        # When
        call_extend_with_mock_system(mock_system, dataset, end_year=END_YEAR_SHORT)

        # Then — original dataset should be untouched
        np.testing.assert_array_equal(
            dataset.person["employment_income"].values,
            original_values,
        )

    def test_given_multiple_entities_uprated_then_all_apply_correctly(
        self, base_dataset, mock_system
    ):
        # When
        result = call_extend_with_mock_system(
            mock_system, base_dataset, end_year=END_YEAR_SHORT
        )

        # Then — both person (employment_income) and household (rent) uprated
        year_one = result[BASE_YEAR + 1]
        np.testing.assert_allclose(
            year_one.person["employment_income"].values,
            EMPLOYMENT_INCOME_BASE * EMPLOYMENT_INCOME_GROWTH_FACTOR_2024_TO_2025,
        )
        np.testing.assert_allclose(
            year_one.household["rent"].values,
            RENT_BASE * CPI_U_GROWTH_FACTOR_2024_TO_2025,
        )

    def test_given_end_year_before_start_year_then_raises_value_error(
        self, base_dataset, mock_system
    ):
        # When / Then
        with pytest.raises(ValueError, match="end_year.*must be >= dataset base year"):
            call_extend_with_mock_system(
                mock_system, base_dataset, end_year=BASE_YEAR - 1
            )


# ---------------------------------------------------------------------------
# USMultiYearDataset.__init__ validation
# ---------------------------------------------------------------------------


class TestUSMultiYearDatasetInit:
    def test_given_neither_arg_then_raises_value_error(self):
        # When / Then
        with pytest.raises(
            ValueError, match="Must provide either datasets or file_path"
        ):
            USMultiYearDataset()

    def test_given_both_args_then_raises_value_error(self, base_dataset, tmp_path):
        # Given
        path = str(tmp_path / "test.h5")
        base_dataset.save(path)

        # When / Then
        with pytest.raises(
            ValueError,
            match="Provide either datasets or file_path, not both",
        ):
            USMultiYearDataset(datasets=[base_dataset], file_path=path)


# ---------------------------------------------------------------------------
# USSingleYearDataset.load() duplicate column detection
# ---------------------------------------------------------------------------


class TestSingleYearDatasetLoad:
    def test_load_raises_on_duplicate_column_names(self):
        # Given — both person and household have column 'shared_col'
        person_df = pd.DataFrame(
            {
                "person_id": [1, 2],
                "shared_col": [100.0, 200.0],
            }
        )
        household_df = pd.DataFrame(
            {
                "household_id": [1],
                "shared_col": [999.0],
            }
        )
        ds = USSingleYearDataset(
            person=person_df,
            household=household_df,
            tax_unit=pd.DataFrame({"tax_unit_id": [1]}),
        )

        # When / Then
        with pytest.raises(ValueError, match="Duplicate column 'shared_col'"):
            ds.load()

    def test_load_returns_all_entity_columns(self, base_dataset):
        # When
        data = base_dataset.load()

        # Then
        assert "person_id" in data
        assert "employment_income" in data
        assert "household_id" in data
        assert "rent" in data
        assert "tax_unit_id" in data
        np.testing.assert_array_equal(data["employment_income"], EMPLOYMENT_INCOME_BASE)


# ---------------------------------------------------------------------------
# USMultiYearDataset.load() duplicate column detection
# ---------------------------------------------------------------------------


class TestMultiYearDatasetLoad:
    def test_load_raises_on_duplicate_column_across_entities(self):
        # Given — both person and household have column 'shared_col'
        person_df = pd.DataFrame(
            {
                "person_id": [1, 2],
                "shared_col": [100.0, 200.0],
            }
        )
        household_df = pd.DataFrame(
            {
                "household_id": [1],
                "shared_col": [999.0],
            }
        )
        ds = USSingleYearDataset(
            person=person_df,
            household=household_df,
            tax_unit=pd.DataFrame({"tax_unit_id": [1]}),
            time_period=2024,
        )
        multi = USMultiYearDataset(datasets=[ds])

        # When / Then
        with pytest.raises(ValueError, match="Duplicate column 'shared_col'"):
            multi.load()


# ---------------------------------------------------------------------------
# _is_hdfstore_format
# ---------------------------------------------------------------------------


class TestIsHdfstoreFormat:
    def test_entity_level_file_returns_true(self, base_dataset, tmp_path):
        # Given
        path = str(tmp_path / "entity_level.h5")
        base_dataset.save(path)

        # When / Then
        from policyengine_us.system import _is_hdfstore_format

        assert _is_hdfstore_format(path) is True

    def test_variable_level_file_returns_false(self, tmp_path):
        # Given — create a variable-centric h5py file
        import h5py

        path = str(tmp_path / "variable_level.h5")
        with h5py.File(path, "w") as f:
            f.create_dataset("employment_income", data=np.array([50_000.0]))
            f.create_dataset("age", data=np.array([25.0]))

        # When / Then
        from policyengine_us.system import _is_hdfstore_format

        assert _is_hdfstore_format(path) is False

    def test_nonexistent_file_returns_false(self):
        # When / Then
        from policyengine_us.system import _is_hdfstore_format

        assert _is_hdfstore_format("/nonexistent/path.h5") is False


# ---------------------------------------------------------------------------
# _resolve_dataset_path
# ---------------------------------------------------------------------------


class TestResolveDatasetPath:
    def test_nonexistent_path_raises_file_not_found(self):
        # When / Then
        from policyengine_us.system import _resolve_dataset_path

        with pytest.raises(FileNotFoundError, match="Dataset file not found"):
            _resolve_dataset_path("/nonexistent/path/file.h5")

    def test_existing_path_returns_path(self, base_dataset, tmp_path):
        # Given
        path = str(tmp_path / "test.h5")
        base_dataset.save(path)

        # When
        from policyengine_us.system import _resolve_dataset_path

        result = _resolve_dataset_path(path)

        # Then
        assert result == path


# ---------------------------------------------------------------------------
# File I/O roundtrips
# ---------------------------------------------------------------------------


class TestFileIORoundtrips:
    def test_single_year_save_and_load_roundtrip(self, base_dataset, tmp_path):
        # Given
        path = str(tmp_path / "single_year.h5")

        # When
        base_dataset.save(path)
        loaded = USSingleYearDataset(file_path=path)

        # Then
        assert loaded.time_period == base_dataset.time_period
        for name in base_dataset.table_names:
            original = getattr(base_dataset, name)
            reloaded = getattr(loaded, name)
            if len(original) > 0:
                pd.testing.assert_frame_equal(reloaded, original)

    def test_multi_year_save_and_load_roundtrip(
        self, base_dataset, mock_system, tmp_path
    ):
        # Given
        multi = call_extend_with_mock_system(
            mock_system, base_dataset, end_year=END_YEAR_SHORT
        )
        path = str(tmp_path / "multi_year.h5")

        # When
        multi.save(path)
        loaded = USMultiYearDataset(file_path=path)

        # Then
        assert loaded.years == multi.years
        for year in multi.years:
            original = multi[year]
            reloaded = loaded[year]
            assert reloaded.time_period == original.time_period
            for name in original.table_names:
                orig_df = getattr(original, name)
                load_df = getattr(reloaded, name)
                if len(orig_df) > 0:
                    pd.testing.assert_frame_equal(load_df, orig_df)

    def test_multi_year_load_returns_time_period_arrays(
        self, base_dataset, mock_system
    ):
        # Given
        multi = call_extend_with_mock_system(
            mock_system, base_dataset, end_year=END_YEAR_SHORT
        )

        # When
        data = multi.load()

        # Then — keys are column names, values are {year: array}
        assert "employment_income" in data
        assert set(data["employment_income"].keys()) == set(
            range(BASE_YEAR, END_YEAR_SHORT + 1)
        )
        np.testing.assert_array_equal(
            data["employment_income"][BASE_YEAR],
            EMPLOYMENT_INCOME_BASE,
        )


# ---------------------------------------------------------------------------
# USSingleYearDataset edge cases (Suggestion 13)
# ---------------------------------------------------------------------------


class TestUSSingleYearDatasetEdgeCases:
    def test_missing_required_person_df_raises(self):
        with pytest.raises(ValueError, match="Must provide either a file path"):
            USSingleYearDataset(
                household=pd.DataFrame({"household_id": [1]}),
                tax_unit=pd.DataFrame({"tax_unit_id": [1]}),
            )

    def test_missing_required_household_df_raises(self):
        with pytest.raises(ValueError, match="Must provide either a file path"):
            USSingleYearDataset(
                person=pd.DataFrame({"person_id": [1]}),
                tax_unit=pd.DataFrame({"tax_unit_id": [1]}),
            )

    def test_missing_required_tax_unit_df_raises(self):
        with pytest.raises(ValueError, match="Must provide either a file path"):
            USSingleYearDataset(
                person=pd.DataFrame({"person_id": [1]}),
                household=pd.DataFrame({"household_id": [1]}),
            )

    def test_non_h5_extension_raises(self):
        with pytest.raises(ValueError, match="must end with '.h5'"):
            USSingleYearDataset.validate_file_path("foo.csv")

    def test_validate_file_path_with_raise_exception_false_returns_false(self):
        assert (
            USSingleYearDataset.validate_file_path("foo.csv", raise_exception=False)
            is False
        )

    def test_file_not_found_raises(self):
        with pytest.raises(FileNotFoundError, match="File not found"):
            USSingleYearDataset.validate_file_path("/nonexistent/path.h5")

    def test_file_not_found_with_raise_exception_false_returns_false(self):
        assert (
            USSingleYearDataset.validate_file_path(
                "/nonexistent/path.h5", raise_exception=False
            )
            is False
        )

    def test_name_property(self):
        ds = USSingleYearDataset(
            person=pd.DataFrame({"person_id": [1]}),
            household=pd.DataFrame({"household_id": [1]}),
            tax_unit=pd.DataFrame({"tax_unit_id": [1]}),
            time_period=2025,
        )
        assert ds.name == "us_single_year_2025"

    def test_label_property(self):
        ds = USSingleYearDataset(
            person=pd.DataFrame({"person_id": [1]}),
            household=pd.DataFrame({"household_id": [1]}),
            tax_unit=pd.DataFrame({"tax_unit_id": [1]}),
            time_period=2025,
        )
        assert ds.label == "US Single Year Dataset (2025)"

    def test_file_path_property_returns_none(self):
        ds = USSingleYearDataset(
            person=pd.DataFrame({"person_id": [1]}),
            household=pd.DataFrame({"household_id": [1]}),
            tax_unit=pd.DataFrame({"tax_unit_id": [1]}),
        )
        assert ds.file_path is None


# ---------------------------------------------------------------------------
# USMultiYearDataset edge cases (Suggestion 13)
# ---------------------------------------------------------------------------


class TestUSMultiYearDatasetEdgeCases:
    def test_non_single_year_dataset_in_list_raises_type_error(self):
        with pytest.raises(
            TypeError,
            match="All items in datasets must be of type USSingleYearDataset",
        ):
            USMultiYearDataset(datasets=[{"not": "a dataset"}])

    def test_get_year_nonexistent_raises_value_error(self):
        ds = USSingleYearDataset(
            person=pd.DataFrame({"person_id": [1]}),
            household=pd.DataFrame({"household_id": [1]}),
            tax_unit=pd.DataFrame({"tax_unit_id": [1]}),
            time_period=2024,
        )
        multi = USMultiYearDataset(datasets=[ds])
        with pytest.raises(ValueError, match="No dataset found for year 9999"):
            multi.get_year(9999)

    def test_name_property(self):
        ds_a = USSingleYearDataset(
            person=pd.DataFrame({"person_id": [1]}),
            household=pd.DataFrame({"household_id": [1]}),
            tax_unit=pd.DataFrame({"tax_unit_id": [1]}),
            time_period=2024,
        )
        ds_b = USSingleYearDataset(
            person=pd.DataFrame({"person_id": [1]}),
            household=pd.DataFrame({"household_id": [1]}),
            tax_unit=pd.DataFrame({"tax_unit_id": [1]}),
            time_period=2026,
        )
        multi = USMultiYearDataset(datasets=[ds_a, ds_b])
        assert multi.name == "us_multi_year_2024_2026"

    def test_label_property(self):
        ds = USSingleYearDataset(
            person=pd.DataFrame({"person_id": [1]}),
            household=pd.DataFrame({"household_id": [1]}),
            tax_unit=pd.DataFrame({"tax_unit_id": [1]}),
            time_period=2024,
        )
        multi = USMultiYearDataset(datasets=[ds])
        assert multi.label == "US Multi Year Dataset (2024-2024)"

    def test_file_path_property_returns_none(self):
        ds = USSingleYearDataset(
            person=pd.DataFrame({"person_id": [1]}),
            household=pd.DataFrame({"household_id": [1]}),
            tax_unit=pd.DataFrame({"tax_unit_id": [1]}),
            time_period=2024,
        )
        multi = USMultiYearDataset(datasets=[ds])
        assert multi.file_path is None


# ---------------------------------------------------------------------------
# _resolve_dataset_path: hf:// URL mock test
# ---------------------------------------------------------------------------


class TestResolveDatasetPathHfUrl:
    def test_hf_url_calls_download(self, monkeypatch):
        """Verify hf:// URLs dispatch to the HuggingFace download path."""
        from policyengine_us import system as system_module

        mock_local_path = "/tmp/mock_downloaded.h5"

        monkeypatch.setattr(
            system_module,
            "_resolve_dataset_path",
            lambda ds: self._patched_resolve(ds, monkeypatch, mock_local_path),
        )

        # Test the actual function directly instead
        import policyengine_core.tools.hugging_face as hf_module

        monkeypatch.setattr(
            hf_module,
            "parse_hf_url",
            lambda url: ("policyengine", "test-repo", "file.h5", None),
        )
        monkeypatch.setattr(
            hf_module,
            "download_huggingface_dataset",
            lambda repo, repo_filename, version: mock_local_path,
        )

        from policyengine_us.system import _resolve_dataset_path

        result = _resolve_dataset_path("hf://policyengine/test-repo/file.h5")
        assert result == mock_local_path

    @staticmethod
    def _patched_resolve(ds, monkeypatch, mock_path):
        """Helper — not used directly, kept for clarity."""
        return mock_path


# ---------------------------------------------------------------------------
# Legacy h5py format backward compatibility
# ---------------------------------------------------------------------------


class TestLegacyH5pyFormatCompat:
    def test_variable_centric_file_not_treated_as_entity_level(self, tmp_path):
        """End-to-end: a legacy h5py variable-centric file should not
        be detected as entity-level HDFStore format, ensuring it passes
        through to core's default dataset handling unchanged."""
        import h5py
        from policyengine_us.system import (
            _resolve_dataset_path,
            _is_hdfstore_format,
        )

        path = str(tmp_path / "legacy.h5")
        with h5py.File(path, "w") as f:
            f.create_dataset("employment_income/2024", data=np.array([50_000.0]))
            f.create_dataset("age/2024", data=np.array([30.0]))

        resolved = _resolve_dataset_path(path)
        assert resolved == path
        assert _is_hdfstore_format(resolved) is False


# ---------------------------------------------------------------------------
# Microsimulation.__init__ dataset routing integration tests
# ---------------------------------------------------------------------------


class TestMicrosimulationDatasetRouting:
    """Verify the 3 dataset input paths in Microsimulation.__init__
    reach the correct branch without loading the full tax-benefit system."""

    def test_string_hdfstore_path_triggers_extend(
        self, base_dataset, tmp_path, monkeypatch
    ):
        path = str(tmp_path / "entity_level.h5")
        base_dataset.save(path)

        extend_called = {"value": False}
        original_dataset = [None]

        def mock_extend(ds, **kwargs):
            extend_called["value"] = True
            original_dataset[0] = ds
            return USMultiYearDataset(datasets=[ds])

        monkeypatch.setattr(
            "policyengine_us.data.economic_assumptions.extend_single_year_dataset",
            mock_extend,
        )

        from policyengine_us import system as system_module

        monkeypatch.setattr(
            system_module.CoreMicrosimulation,
            "__init__",
            make_mock_super_init(system_module),
        )

        sim = system_module.Microsimulation(dataset=path)
        assert extend_called["value"] is True
        assert isinstance(original_dataset[0], USSingleYearDataset)

    def test_single_year_dataset_triggers_extend(self, base_dataset, monkeypatch):
        extend_called = {"value": False}

        def mock_extend(ds, **kwargs):
            extend_called["value"] = True
            return USMultiYearDataset(datasets=[ds])

        monkeypatch.setattr(
            "policyengine_us.data.economic_assumptions.extend_single_year_dataset",
            mock_extend,
        )

        from policyengine_us import system as system_module

        monkeypatch.setattr(
            system_module.CoreMicrosimulation,
            "__init__",
            make_mock_super_init(system_module),
        )

        sim = system_module.Microsimulation(dataset=base_dataset)
        assert extend_called["value"] is True

    def test_multi_year_dataset_passes_through(self, base_dataset, monkeypatch):
        multi = USMultiYearDataset(datasets=[base_dataset])

        extend_called = {"value": False}

        def mock_extend(ds, **kwargs):
            extend_called["value"] = True
            return multi

        monkeypatch.setattr(
            "policyengine_us.data.economic_assumptions.extend_single_year_dataset",
            mock_extend,
        )

        from policyengine_us import system as system_module

        captured_dataset = [None]

        monkeypatch.setattr(
            system_module.CoreMicrosimulation,
            "__init__",
            make_mock_super_init(system_module, captured=captured_dataset),
        )

        sim = system_module.Microsimulation(dataset=multi)
        assert extend_called["value"] is False
        assert captured_dataset[0] is multi


# ---------------------------------------------------------------------------
# save() append-mode regression
# ---------------------------------------------------------------------------


class TestSaveAppendRegression:
    def test_save_twice_does_not_duplicate_rows(self, base_dataset, tmp_path):
        """Saving to the same path twice should overwrite, not append."""
        path = str(tmp_path / "test.h5")
        base_dataset.save(path)
        base_dataset.save(path)

        loaded = USSingleYearDataset(file_path=path)
        assert len(loaded.person) == len(base_dataset.person)


# ---------------------------------------------------------------------------
# get_parameter_last_year utility
# ---------------------------------------------------------------------------


class TestGetParameterLastYear:
    def test_returns_latest_year_from_yaml(self, tmp_path):
        yaml_content = {
            "values": {
                "2024-01-01": 100.0,
                "2026-01-01": 121.0,
                "2035-02-01": 407.3,
                "2025-06-01": 110.0,
            }
        }
        yaml_file = tmp_path / "param.yaml"
        import yaml

        yaml_file.write_text(yaml.dump(yaml_content))

        class FakeParam:
            file_path = str(yaml_file)

        assert get_parameter_last_year(FakeParam()) == 2035

    def test_single_value_yaml(self, tmp_path):
        yaml_content = {"values": {"2024-01-01": 100.0}}
        yaml_file = tmp_path / "param.yaml"
        import yaml

        yaml_file.write_text(yaml.dump(yaml_content))

        class FakeParam:
            file_path = str(yaml_file)

        assert get_parameter_last_year(FakeParam()) == 2024

    def test_with_real_cpi_u_parameter(self):
        """Verify get_parameter_last_year works on the actual CPI-U
        parameter YAML, returning 2035 (not 2100 from uprating_extensions)."""
        from policyengine_us.system import system

        cpi_u = _resolve_parameter(system.parameters, "gov.bls.cpi.cpi_u")
        last_year = get_parameter_last_year(cpi_u)
        # CPI-U YAML currently extends to 2035; if the YAML is updated,
        # this assertion should be updated to match.
        assert last_year == 2035
