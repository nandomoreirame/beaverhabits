"""Extended API for desktop widgets (fork addition).

Kept apart from routes/api.py so upstream merges stay conflict-free.
Dates use ISO format (YYYY-MM-DD).
"""

import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from beaverhabits import views
from beaverhabits.app.db import User
from beaverhabits.app.dependencies import current_active_user
from beaverhabits.configs import settings
from beaverhabits.core.summary import count_between, current_streak, longest_streak
from beaverhabits.storage.storage import (
    Habit,
    HabitList,
    HabitListBuilder,
    HabitListNotFoundError,
    HabitStatus,
)

MAX_BATCH_TICKS = 100

ext_router = APIRouter(tags=["ext"])


def server_today() -> datetime.date:
    zone = ZoneInfo(settings.TIME_ZONE) if settings.TIME_ZONE else datetime.UTC
    return datetime.datetime.now(zone).date()


def resolve_day(day: datetime.date | None) -> datetime.date:
    return day or server_today()


async def load_habit_list(user: User) -> HabitList | None:
    """A user without any habit yet has no stored list: treat it as empty."""
    try:
        return await views.user_storage.get_user_habit_list(user)
    except HabitListNotFoundError:
        return None


def habit_day_state(habit: Habit, day: datetime.date) -> dict:
    record = habit.record_by(day)
    return {
        "id": habit.id,
        "name": habit.name,
        "star": bool(habit.star),
        "tags": list(habit.tags),
        "done": bool(record and record.done),
        "note": (record.text if record else "") or "",
        "streak": current_streak(habit.ticked_days, day),
    }


@ext_router.get("/today")
async def get_today(
    date: datetime.date | None = Query(default=None),
    user: User = Depends(current_active_user),
):
    day = resolve_day(date)
    habit_list = await load_habit_list(user)
    habits = (
        HabitListBuilder(habit_list).status(HabitStatus.ACTIVE).build()
        if habit_list
        else []
    )
    states = [habit_day_state(habit, day) for habit in habits]
    return {
        "date": day.isoformat(),
        "total": len(states),
        "done": sum(1 for s in states if s["done"]),
        "habits": states,
    }


class BatchTick(BaseModel):
    habit_id: str = Field(min_length=1, max_length=64)
    date: datetime.date
    done: bool
    text: str | None = Field(default=None, max_length=settings.DAILY_NOTE_MAX_LENGTH)


class BatchTicks(BaseModel):
    ticks: list[BatchTick] = Field(min_length=1, max_length=MAX_BATCH_TICKS)


@ext_router.post("/ticks")
async def post_ticks(
    payload: BatchTicks,
    user: User = Depends(current_active_user),
):
    habit_list = await load_habit_list(user)
    if habit_list is None:
        raise HTTPException(status_code=404, detail="Habit not found")

    # Resolve every habit before writing, so an unknown id applies nothing.
    resolved: list[tuple[Habit, BatchTick]] = []
    for item in payload.ticks:
        habit = await habit_list.get_habit_by(item.habit_id)
        if habit is None:
            raise HTTPException(status_code=404, detail="Habit not found")
        resolved.append((habit, item))

    applied = []
    for habit, item in resolved:
        await habit.tick(item.date, item.done, item.text)
        applied.append(
            {
                "habit_id": item.habit_id,
                "date": item.date.isoformat(),
                "done": item.done,
            }
        )
    return {"applied": applied}


@ext_router.get("/habits/{habit_id}/summary")
async def get_habit_summary(
    habit_id: str,
    date: datetime.date | None = Query(default=None),
    user: User = Depends(current_active_user),
):
    day = resolve_day(date)
    habit = await views.get_user_habit(user, habit_id)
    done_days = [d for d in habit.ticked_days if d <= day]
    return {
        "id": habit.id,
        "name": habit.name,
        "date": day.isoformat(),
        "streak": current_streak(done_days, day),
        "longest_streak": longest_streak(done_days, day),
        "last_7_days": count_between(done_days, day - datetime.timedelta(days=6), day),
        "last_30_days": count_between(
            done_days, day - datetime.timedelta(days=29), day
        ),
        "total": len(set(done_days)),
        "last_done": max(done_days).isoformat() if done_days else None,
    }


def init_ext_api_routes(app: FastAPI) -> None:
    app.include_router(ext_router, prefix="/api/v1/ext")
