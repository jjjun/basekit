import pytest

from basekit.discovery import (
    DiscoveryError,
    DiscoveryFailure,
    import_packages,
    normalize_paths,
    validate_package_security,
)


def test_normalize_paths_accepts_single_string():
    assert normalize_paths("path1") == ["path1"]


def test_normalize_paths_accepts_comma_separated_string():
    assert normalize_paths("path1,path2,path3") == ["path1", "path2", "path3"]


def test_normalize_paths_accepts_list():
    assert normalize_paths(["path1", "path2"]) == ["path1", "path2"]


def test_normalize_paths_accepts_none():
    assert normalize_paths(None) == []


def test_normalize_paths_strips_whitespace():
    assert normalize_paths("  path1  , path2  ,  ") == ["path1", "path2"]


def test_discovery_failure_to_dict():
    failure = DiscoveryFailure(
        target="myapp.routes",
        target_type="package",
        exception_type="ImportError",
        message="Not found",
    )

    assert failure.to_dict() == {
        "target": "myapp.routes",
        "target_type": "package",
        "exception_type": "ImportError",
        "message": "Not found",
    }


def test_discovery_error_contains_failures():
    failures = [
        DiscoveryFailure("myapp.routes", "package", "ImportError", "Not found")
    ]

    error = DiscoveryError(failures)

    assert "Discovery failed with 1 error(s)" in str(error)
    assert error.failures == tuple(failures)


def test_validate_package_security_rejects_disallowed_package():
    with pytest.raises(ValueError, match="Security"):
        validate_package_security("os", allowed_prefixes={"myapp."})


def test_import_packages_imports_valid_package():
    assert import_packages("os") == []


def test_import_packages_collects_failures():
    failures = import_packages(["os", "nonexistent_package_12345"])

    assert len(failures) == 1
    assert failures[0].target == "nonexistent_package_12345"
    assert failures[0].exception_type == "ModuleNotFoundError"


def test_import_packages_can_raise_discovery_error():
    with pytest.raises(DiscoveryError):
        import_packages("nonexistent_package_12345", fail_on_error=True)
