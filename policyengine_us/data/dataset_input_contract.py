from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


DatasetInputKind = Literal[
    "stochastic_status",
    "medical_status",
    "geographic_status",
    "identifier_status",
    "income_override",
    "deprecated_alias",
]


@dataclass(frozen=True)
class DatasetInputMetadata:
    """Metadata for variables datasets may intentionally provide."""

    variable: str
    kind: DatasetInputKind
    rationale: str


_DATASET_INPUT_METADATA: dict[str, DatasetInputMetadata] = {
    "takes_up_aca_if_eligible": DatasetInputMetadata(
        variable="takes_up_aca_if_eligible",
        kind="stochastic_status",
        rationale="Dataset builders may model ACA take-up among eligible tax units.",
    ),
    "takes_up_basic_health_program_if_eligible": DatasetInputMetadata(
        variable="takes_up_basic_health_program_if_eligible",
        kind="stochastic_status",
        rationale=(
            "Dataset builders may model Basic Health Program take-up among "
            "eligible people."
        ),
    ),
    "takes_up_chip_if_eligible": DatasetInputMetadata(
        variable="takes_up_chip_if_eligible",
        kind="stochastic_status",
        rationale="Dataset builders may model CHIP take-up among eligible people.",
    ),
    "takes_up_dc_ptc": DatasetInputMetadata(
        variable="takes_up_dc_ptc",
        kind="stochastic_status",
        rationale=(
            "Dataset builders may model DC property tax credit take-up among "
            "eligible tax units."
        ),
    ),
    "takes_up_early_head_start_if_eligible": DatasetInputMetadata(
        variable="takes_up_early_head_start_if_eligible",
        kind="stochastic_status",
        rationale=(
            "Dataset builders may model Early Head Start take-up among eligible people."
        ),
    ),
    "takes_up_eitc": DatasetInputMetadata(
        variable="takes_up_eitc",
        kind="stochastic_status",
        rationale="Dataset builders may model EITC take-up among eligible tax units.",
    ),
    "takes_up_head_start_if_eligible": DatasetInputMetadata(
        variable="takes_up_head_start_if_eligible",
        kind="stochastic_status",
        rationale="Dataset builders may model Head Start take-up among eligible people.",
    ),
    "takes_up_housing_assistance_if_eligible": DatasetInputMetadata(
        variable="takes_up_housing_assistance_if_eligible",
        kind="stochastic_status",
        rationale=(
            "Dataset builders may model housing assistance take-up among "
            "eligible SPM units."
        ),
    ),
    "takes_up_medicaid_if_eligible": DatasetInputMetadata(
        variable="takes_up_medicaid_if_eligible",
        kind="stochastic_status",
        rationale="Dataset builders may model Medicaid take-up among eligible people.",
    ),
    "takes_up_medicare_if_eligible": DatasetInputMetadata(
        variable="takes_up_medicare_if_eligible",
        kind="stochastic_status",
        rationale="Dataset builders may model Medicare take-up among eligible people.",
    ),
    "takes_up_snap_if_eligible": DatasetInputMetadata(
        variable="takes_up_snap_if_eligible",
        kind="stochastic_status",
        rationale="Dataset builders may model SNAP take-up among eligible SPM units.",
    ),
    "takes_up_ssi_if_eligible": DatasetInputMetadata(
        variable="takes_up_ssi_if_eligible",
        kind="stochastic_status",
        rationale="Dataset builders may model SSI take-up among eligible people.",
    ),
    "takes_up_tanf_if_eligible": DatasetInputMetadata(
        variable="takes_up_tanf_if_eligible",
        kind="stochastic_status",
        rationale="Dataset builders may model TANF take-up among eligible SPM units.",
    ),
    "would_claim_wic": DatasetInputMetadata(
        variable="would_claim_wic",
        kind="stochastic_status",
        rationale="Dataset builders may model WIC claiming among eligible people.",
    ),
    "is_wic_at_nutritional_risk": DatasetInputMetadata(
        variable="is_wic_at_nutritional_risk",
        kind="medical_status",
        rationale=(
            "Dataset builders may model WIC nutritional-risk status; the model "
            "uses the input directly."
        ),
    ),
    "meets_ssi_disability_criteria": DatasetInputMetadata(
        variable="meets_ssi_disability_criteria",
        kind="medical_status",
        rationale=(
            "Dataset builders may provide the SSI medical-disability criterion "
            "separately from broad disability flags."
        ),
    ),
    "has_tin": DatasetInputMetadata(
        variable="has_tin",
        kind="identifier_status",
        rationale=(
            "Dataset builders may provide taxpayer identification status; the "
            "fallback formula defaults to True when no data are supplied."
        ),
    ),
    "has_itin": DatasetInputMetadata(
        variable="has_itin",
        kind="deprecated_alias",
        rationale=(
            "Deprecated alias accepted during migration from has_itin to has_tin."
        ),
    ),
    "in_nyc": DatasetInputMetadata(
        variable="in_nyc",
        kind="geographic_status",
        rationale=(
            "Dataset builders may provide NYC residency directly when county "
            "geography is unavailable or deliberately suppressed."
        ),
    ),
    "fsla_overtime_premium": DatasetInputMetadata(
        variable="fsla_overtime_premium",
        kind="income_override",
        rationale=(
            "Dataset builders may provide measured or imputed FLSA overtime "
            "premium income instead of relying on weekly-hours approximations."
        ),
    ),
}


def dataset_input_metadata() -> dict[str, DatasetInputMetadata]:
    """Return metadata for variables datasets may intentionally provide."""
    return dict(_DATASET_INPUT_METADATA)


def dataset_input_variables(
    *,
    kind: DatasetInputKind | None = None,
) -> frozenset[str]:
    """Return variables that are explicit dataset inputs under the US model."""
    if kind is None:
        return frozenset(_DATASET_INPUT_METADATA)
    return frozenset(
        name
        for name, metadata in _DATASET_INPUT_METADATA.items()
        if metadata.kind == kind
    )


def get_dataset_input_metadata(
    variable_name: str,
) -> DatasetInputMetadata | None:
    """Return dataset-input metadata for a variable, if explicitly defined."""
    return _DATASET_INPUT_METADATA.get(variable_name)


def is_dataset_input_variable(variable_name: str) -> bool:
    """Return whether a variable is an explicit dataset input."""
    return variable_name in _DATASET_INPUT_METADATA


def variable_has_formula(variable) -> bool:
    """Return whether a variable is computed by formula/adds/subtracts logic."""
    return any(
        bool(getattr(variable, attribute, None))
        for attribute in ("formulas", "adds", "subtracts")
    )


def is_formula_owned_variable(variable_name: str, *, system=None) -> bool:
    """Return whether datasets should normally leave a variable to formulas.

    Ordinary input variables are not formula-owned. Formula-backed variables
    listed in ``dataset_input_metadata`` are deliberate dataset overrides and
    therefore also return ``False`` here.
    """
    if system is None:
        from policyengine_us import CountryTaxBenefitSystem

        system = CountryTaxBenefitSystem()

    variable = system.variables.get(variable_name)
    if variable is None:
        raise KeyError(f"Unknown variable: {variable_name}")
    return variable_has_formula(variable) and not is_dataset_input_variable(
        variable_name
    )


def is_dataset_exportable_variable(variable_name: str, *, system=None) -> bool:
    """Return whether a dataset may export the variable as an input column.

    This helper is intended for data-generation packages. It treats ordinary
    model input variables as exportable and also allows the explicit override
    variables documented in ``dataset_input_metadata``. Formula-owned outputs
    should be calculated by PolicyEngine-US rather than persisted in datasets.
    """
    if system is None:
        from policyengine_us import CountryTaxBenefitSystem

        system = CountryTaxBenefitSystem()

    variable = system.variables.get(variable_name)
    if variable is None:
        raise KeyError(f"Unknown variable: {variable_name}")
    return variable.is_input_variable() or is_dataset_input_variable(variable_name)
