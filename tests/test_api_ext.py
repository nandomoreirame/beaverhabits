"""Tests for the fork's extended API (/api/v1/ext) used by desktop widgets."""

from datetime import date, timedelta

from fastapi.testclient import TestClient

from tests.test_apis import (  # noqa: F401  (pytest fixtures)
    access_token,
    auth_headers,
    client_fixture,
    test_user,
)

DAY = date(2026, 11, 21)


def iso(d: date) -> str:
    return d.isoformat()


def create(client: TestClient, headers: dict, name: str) -> str:
    response = client.post("/api/v1/habits", json={"name": name}, headers=headers)
    assert response.status_code == 200
    return response.json()["id"]


def tick(client, headers, habit_id, day, done=True, text=None):
    body = {"done": done, "date": iso(day), "date_fmt": "%Y-%m-%d"}
    if text is not None:
        body["text"] = text
    response = client.post(
        f"/api/v1/habits/{habit_id}/completions", json=body, headers=headers
    )
    assert response.status_code == 200


def test_today_requires_auth(client: TestClient):
    assert client.get("/api/v1/ext/today").status_code == 401


def test_today_returns_all_active_habits_with_day_state(client, auth_headers):
    run = create(client, auth_headers, "Run")
    read = create(client, auth_headers, "Read")
    tick(client, auth_headers, run, DAY, text="5 km")
    tick(client, auth_headers, run, DAY - timedelta(days=1))

    response = client.get(
        "/api/v1/ext/today", params={"date": iso(DAY)}, headers=auth_headers
    )

    assert response.status_code == 200
    body = response.json()
    assert body["date"] == iso(DAY)
    assert body["total"] == 2
    assert body["done"] == 1
    by_id = {h["id"]: h for h in body["habits"]}
    assert by_id[run] | {"tags": []} == {
        "id": run,
        "name": "Run",
        "star": False,
        "tags": [],
        "done": True,
        "note": "5 km",
        "streak": 2,
    }
    assert by_id[read]["done"] is False
    assert by_id[read]["note"] == ""
    assert by_id[read]["streak"] == 0


def test_today_excludes_archived_habits(client, auth_headers):
    keep = create(client, auth_headers, "Keep")
    gone = create(client, auth_headers, "Gone")
    response = client.put(
        f"/api/v1/habits/{gone}", json={"status": "archive"}, headers=auth_headers
    )
    assert response.status_code == 200

    body = client.get(
        "/api/v1/ext/today", params={"date": iso(DAY)}, headers=auth_headers
    ).json()

    ids = [h["id"] for h in body["habits"]]
    assert keep in ids
    assert gone not in ids


def test_today_rejects_invalid_date(client, auth_headers):
    response = client.get(
        "/api/v1/ext/today", params={"date": "21/11/2026"}, headers=auth_headers
    )
    assert response.status_code == 422


def test_today_without_habits_is_empty(client, auth_headers):
    body = client.get(
        "/api/v1/ext/today", params={"date": iso(DAY)}, headers=auth_headers
    ).json()
    assert body == {"date": iso(DAY), "total": 0, "done": 0, "habits": []}


def test_batch_ticks_apply_all(client, auth_headers):
    a = create(client, auth_headers, "A")
    b = create(client, auth_headers, "B")

    response = client.post(
        "/api/v1/ext/ticks",
        json={
            "ticks": [
                {"habit_id": a, "date": iso(DAY), "done": True, "text": "ok"},
                {"habit_id": b, "date": iso(DAY), "done": True},
            ]
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json() == {
        "applied": [
            {"habit_id": a, "date": iso(DAY), "done": True},
            {"habit_id": b, "date": iso(DAY), "done": True},
        ]
    }
    today = client.get(
        "/api/v1/ext/today", params={"date": iso(DAY)}, headers=auth_headers
    ).json()
    assert today["done"] == 2


def test_batch_ticks_can_undo(client, auth_headers):
    a = create(client, auth_headers, "A")
    tick(client, auth_headers, a, DAY)

    response = client.post(
        "/api/v1/ext/ticks",
        json={"ticks": [{"habit_id": a, "date": iso(DAY), "done": False}]},
        headers=auth_headers,
    )

    assert response.status_code == 200
    today = client.get(
        "/api/v1/ext/today", params={"date": iso(DAY)}, headers=auth_headers
    ).json()
    assert today["done"] == 0


def test_batch_ticks_unknown_habit_applies_nothing(client, auth_headers):
    a = create(client, auth_headers, "A")

    response = client.post(
        "/api/v1/ext/ticks",
        json={
            "ticks": [
                {"habit_id": a, "date": iso(DAY), "done": True},
                {"habit_id": "missing", "date": iso(DAY), "done": True},
            ]
        },
        headers=auth_headers,
    )

    assert response.status_code == 404
    today = client.get(
        "/api/v1/ext/today", params={"date": iso(DAY)}, headers=auth_headers
    ).json()
    assert today["done"] == 0


def test_batch_ticks_limits_size(client, auth_headers):
    a = create(client, auth_headers, "A")
    ticks = [{"habit_id": a, "date": iso(DAY), "done": True}] * 101
    response = client.post(
        "/api/v1/ext/ticks", json={"ticks": ticks}, headers=auth_headers
    )
    assert response.status_code == 422


def test_batch_ticks_rejects_empty_list(client, auth_headers):
    response = client.post(
        "/api/v1/ext/ticks", json={"ticks": []}, headers=auth_headers
    )
    assert response.status_code == 422


def test_batch_ticks_rejects_long_note(client, auth_headers):
    a = create(client, auth_headers, "A")
    response = client.post(
        "/api/v1/ext/ticks",
        json={
            "ticks": [
                {"habit_id": a, "date": iso(DAY), "done": True, "text": "x" * 5000}
            ]
        },
        headers=auth_headers,
    )
    assert response.status_code == 422


def test_summary_counts_week_month_and_streaks(client, auth_headers):
    a = create(client, auth_headers, "A")
    for offset in (0, 1, 2, 10, 11, 12, 13, 40):
        tick(client, auth_headers, a, DAY - timedelta(days=offset))

    response = client.get(
        f"/api/v1/ext/habits/{a}/summary",
        params={"date": iso(DAY)},
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": a,
        "name": "A",
        "date": iso(DAY),
        "streak": 3,
        "longest_streak": 4,
        "last_7_days": 3,
        "last_30_days": 7,
        "total": 8,
        "last_done": iso(DAY),
    }


def test_summary_unknown_habit_is_404(client, auth_headers):
    response = client.get("/api/v1/ext/habits/missing/summary", headers=auth_headers)
    assert response.status_code == 404
