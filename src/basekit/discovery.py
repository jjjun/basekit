"""Generic package discovery and import helpers."""

import importlib
import logging
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

DEFAULT_EXCLUDED_DIRS = {"__pycache__"}


def normalize_paths(paths: str | list[str] | None, separator: str = ",") -> list[str]:
    """Normalize a string or list of paths/package names to a list."""
    if not paths:
        return []

    if isinstance(paths, str):
        if separator in paths:
            return [part.strip() for part in paths.split(separator) if part.strip()]
        return [paths]

    return list(paths)


@dataclass(frozen=True)
class DiscoveryFailure:
    """Structured discovery/import failure information."""

    target: str
    target_type: Literal["package", "module", "directory", "file"]
    exception_type: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {
            "target": self.target,
            "target_type": self.target_type,
            "exception_type": self.exception_type,
            "message": self.message,
        }


class DiscoveryError(RuntimeError):
    """Raised when discovery fails and fail-on-error behavior is requested."""

    def __init__(self, failures: Sequence[DiscoveryFailure]):
        self.failures = tuple(failures)
        details = "; ".join(
            f"{failure.target_type} '{failure.target}' failed with "
            f"{failure.exception_type}: {failure.message}"
            for failure in self.failures
        )
        super().__init__(
            f"Discovery failed with {len(self.failures)} error(s): {details}"
        )


def validate_package_security(
    package_name: str,
    allowed_prefixes: set[str],
    strict: bool = True,
) -> None:
    """Validate that a package name starts with an allowed prefix."""
    if any(package_name.startswith(prefix) for prefix in allowed_prefixes):
        return

    message = (
        f"Security: Package '{package_name}' is not in allowed list. "
        f"Allowed prefixes: {allowed_prefixes}"
    )
    if strict:
        raise ValueError(message)

    logging.getLogger(__name__).warning(message)


def import_packages(
    package_names: str | list[str] | None,
    allowed_prefixes: set[str] | None = None,
    fail_on_error: bool = False,
) -> list[DiscoveryFailure]:
    """Import packages and return structured failures."""
    packages = normalize_paths(package_names)
    failures: list[DiscoveryFailure] = []

    for package_name in packages:
        try:
            if allowed_prefixes:
                validate_package_security(package_name, allowed_prefixes, strict=True)
            importlib.import_module(package_name)
        except Exception as exc:
            failures.append(
                DiscoveryFailure(
                    target=package_name,
                    target_type="package",
                    exception_type=type(exc).__name__,
                    message=str(exc),
                )
            )

    if failures and fail_on_error:
        raise DiscoveryError(failures)

    return failures


def import_from_directory(
    directory: str | Path,
    base_package: str,
    excluded_dirs: set[str] | None = None,
    fail_on_error: bool = False,
) -> list[DiscoveryFailure]:
    """Import all public Python modules below a directory."""
    excluded_dirs = DEFAULT_EXCLUDED_DIRS if excluded_dirs is None else excluded_dirs
    directory = Path(directory)
    failures: list[DiscoveryFailure] = []

    py_files: list[tuple[Path, Path]] = []
    for py_file in directory.rglob("*.py"):
        if "__pycache__" in py_file.parts:
            continue
        if py_file.stem.startswith("_"):
            continue

        relative_path = py_file.relative_to(directory)
        if any(excluded_dir in relative_path.parts for excluded_dir in excluded_dirs):
            continue

        py_files.append((py_file, relative_path))

    py_files.sort(key=lambda item: str(item[1]))

    for _, relative_path in py_files:
        module_parts = list(relative_path.parts[:-1]) + [relative_path.stem]
        module_name = ".".join(module_parts)
        full_module_name = f"{base_package}.{module_name}" if module_name else base_package

        try:
            importlib.import_module(full_module_name)
        except Exception as exc:
            failures.append(
                DiscoveryFailure(
                    target=full_module_name,
                    target_type="module",
                    exception_type=type(exc).__name__,
                    message=str(exc),
                )
            )

    if failures and fail_on_error:
        raise DiscoveryError(failures)

    return failures


def import_package_directory(
    package_name: str,
    excluded_dirs: set[str] | None = None,
    allowed_prefixes: set[str] | None = None,
    fail_on_error: bool = False,
) -> list[DiscoveryFailure]:
    """Import all public modules below an importable package directory."""
    if allowed_prefixes:
        validate_package_security(package_name, allowed_prefixes, strict=True)

    try:
        package = importlib.import_module(package_name)
        if not hasattr(package, "__path__"):
            raise ValueError(f"{package_name} is not a package (it's a module)")

        package_dir = Path(package.__path__[0])
        return import_from_directory(
            directory=package_dir,
            base_package=package_name,
            excluded_dirs=excluded_dirs,
            fail_on_error=fail_on_error,
        )
    except (ImportError, ValueError) as exc:
        if fail_on_error:
            raise
        return [
            DiscoveryFailure(
                target=package_name,
                target_type="package",
                exception_type=type(exc).__name__,
                message=str(exc),
            )
        ]


def import_from_packages(
    package_names: str | list[str] | None,
    excluded_dirs: set[str] | None = None,
    allowed_prefixes: set[str] | None = None,
    fail_on_error: bool = False,
    post_import_hook: Callable[[], None] | None = None,
) -> list[DiscoveryFailure]:
    """Import modules from multiple packages, then optionally run a hook."""
    packages = normalize_paths(package_names)
    all_failures: list[DiscoveryFailure] = []

    for package_name in packages:
        all_failures.extend(
            import_package_directory(
                package_name=package_name,
                excluded_dirs=excluded_dirs,
                allowed_prefixes=allowed_prefixes,
                fail_on_error=False,
            )
        )

    if post_import_hook:
        try:
            post_import_hook()
        except Exception as exc:
            message = f"Post-import hook failed: {exc}"
            if fail_on_error:
                raise RuntimeError(message) from exc
            logging.getLogger(__name__).warning(message, exc_info=True)

    if all_failures and fail_on_error:
        raise DiscoveryError(all_failures)

    return all_failures


__all__ = [
    "DEFAULT_EXCLUDED_DIRS",
    "DiscoveryError",
    "DiscoveryFailure",
    "import_from_directory",
    "import_from_packages",
    "import_package_directory",
    "import_packages",
    "normalize_paths",
    "validate_package_security",
]
