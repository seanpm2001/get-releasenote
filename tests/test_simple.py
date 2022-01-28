import pathlib

import pytest

from get_releasenote import (
    Context,
    DistInfo,
    analyze_dists,
    check_fix_issue,
    find_version,
)


@pytest.fixture
def root() -> pathlib.Path:
    return pathlib.Path(__file__).parent


#################


def test_check_fix_issue_ok1() -> None:
    assert check_fix_issue("s1", "s2") is None


def test_check_fix_issue_ok2() -> None:
    assert check_fix_issue("", "") is None


def test_check_fix_issue_fail1() -> None:
    with pytest.raises(ValueError):
        assert check_fix_issue("", "s2")


def test_check_fix_issue_fail2() -> None:
    with pytest.raises(ValueError):
        assert check_fix_issue("s1", "")


##################


@pytest.fixture
def dist(root: pathlib.Path) -> DistInfo:
    return analyze_dists(root, "dist_ok")


@pytest.fixture
def ctx(tmp_path: pathlib.Path, dist: DistInfo) -> Context:
    return Context(tmp_path, dist)


def test_find_version_autodetected(ctx: Context) -> None:
    assert "0.0.7" == find_version(ctx, "", "")


def test_find_version_ambigous(ctx: Context) -> None:
    with pytest.raises(ValueError, match="ambiguous"):
        (ctx.root / "file.py").write_text("__version__='1.2.3'")
        find_version(ctx, "file.py", "3.4.5")


def test_find_version_mismatch_with_autodetected(ctx: Context) -> None:
    with pytest.raises(ValueError, match="mismatches with autodetected "):
        find_version(ctx, "", "1.2.3")


def test_find_version_explicit(ctx: Context) -> None:
    assert "0.0.7" == find_version(ctx, "", "0.0.7")


def test_find_version_file_mismatch_with_autodetected(ctx: Context) -> None:
    with pytest.raises(ValueError, match="mismatches with autodetected "):
        (ctx.root / "file.py").write_text("__version__='1.2.3'")
        find_version(ctx, "file.py", "")


def test_find___version___no_spaces(ctx: Context) -> None:
    (ctx.root / "file.py").write_text("__version__='0.0.7'")
    assert "0.0.7" == find_version(ctx, "file.py", "")


def test_find___version___from_file_single_quotes(ctx: Context) -> None:
    (ctx.root / "file.py").write_text("__version__ = '0.0.7'")
    assert "0.0.7" == find_version(ctx, "file.py", "")


def test_find___version___from_file_double_quotes(ctx: Context) -> None:
    (ctx.root / "file.py").write_text('__version__ = "0.0.7"')
    assert "0.0.7" == find_version(ctx, "file.py", "")


def test_find_version_from_file_single_quotes(ctx: Context) -> None:
    (ctx.root / "file.py").write_text("version = '0.0.7'")
    assert "0.0.7" == find_version(ctx, "file.py", "")


def test_find_version_from_file_double_quotes(ctx: Context) -> None:
    (ctx.root / "file.py").write_text('version = "0.0.7"')
    assert "0.0.7" == find_version(ctx, "file.py", "")


def test_find_version_not_found(ctx: Context) -> None:
    (ctx.root / "file.py").write_text("not_a_version = '0.0.7'")
    with pytest.raises(ValueError, match="Unable to determine version"):
        find_version(ctx, "file.py", "")
