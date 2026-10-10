from datetime import date

import pytest

from src.db.history import CsvHistory, SqlHistory, open_history


@pytest.fixture(params=["csv", "sql"])
def history(request, tmp_path):
    if request.param == "csv":
        return CsvHistory(str(tmp_path / "history"))
    return SqlHistory(f"sqlite:///{tmp_path}/history.db")


def test_no_history_returns_none(history):
    assert history.load_previous("ml", before=date(2026, 1, 8)) is None


def test_loads_most_recent_earlier_snapshot(history, previous_df, current_df):
    history.save(previous_df, "ml", date(2026, 1, 1))
    history.save(current_df, "ml", date(2026, 1, 8))
    history.save(current_df, "other topic", date(2026, 1, 9))

    prev = history.load_previous("ml", before=date(2026, 1, 8))
    assert set(prev["full_name"]) == {"org/alpha", "org/beta", "solo/gone"}
    assert prev.loc[prev["full_name"] == "org/beta", "stargazers_count"].item() == 5_000
    assert prev["snapshot_date"].iloc[0] == "2026-01-01"

    assert len(history.load_previous("ml", before=date(2026, 1, 15))) == len(current_df)


def test_same_day_rerun_overwrites(history, previous_df, current_df):
    # A manual re-run must not leave two snapshots for one day (or compare a week against itself).
    history.save(previous_df, "ml", date(2026, 1, 1))
    history.save(current_df, "ml", date(2026, 1, 1))
    prev = history.load_previous("ml", before=date(2026, 1, 2))
    assert len(prev) == len(current_df)


def test_csv_snapshot_is_small(tmp_path, current_df):
    CsvHistory(str(tmp_path)).save(current_df, "machine learning", date(2026, 1, 1))
    text = (tmp_path / "machine_learning" / "2026-01-01.csv").read_text()
    assert text.splitlines()[0] == "full_name,stargazers_count,forks_count"
    assert "description" not in text


def test_open_history_picks_backend(tmp_path):
    assert isinstance(open_history(None, str(tmp_path)), CsvHistory)
    assert isinstance(open_history(f"sqlite:///{tmp_path}/x.db", str(tmp_path)), SqlHistory)
