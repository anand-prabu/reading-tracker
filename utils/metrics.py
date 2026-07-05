import pandas as pd
from datetime import date, timedelta
from utils.models import ReadingLog, LevelDefinition, UserBadge


def _to_date(val):
    if isinstance(val, date):
        return val
    try:
        return pd.Timestamp(val).date()
    except Exception:
        return None


def get_logs_df(session, user_id):
    try:
        from utils.models import Book
        rows = (
            session.query(
                ReadingLog.log_date,
                ReadingLog.pages_read,
                ReadingLog.minutes_spent,
                ReadingLog.book_id,
                Book.title.label("book_title"),
            )
            .join(Book, Book.id == ReadingLog.book_id)
            .filter(ReadingLog.user_id == user_id)
            .order_by(ReadingLog.log_date.asc())
            .all()
        )
        if not rows:
            return pd.DataFrame(columns=[
                "log_date", "pages_read",
                "minutes_spent", "book_id", "book_title"
            ])
        df = pd.DataFrame(rows, columns=[
            "log_date", "pages_read",
            "minutes_spent", "book_id", "book_title"
        ])
        df["log_date"] = df["log_date"].apply(_to_date)
        return df
    except Exception:
        return pd.DataFrame(columns=[
            "log_date", "pages_read",
            "minutes_spent", "book_id", "book_title"
        ])


def current_streak(df):
    if df is None or df.empty:
        return 0
    unique_days = sorted(
        set(df["log_date"].apply(_to_date).dropna()),
        reverse=True
    )
    if not unique_days:
        return 0
    today     = date.today()
    yesterday = today - timedelta(days=1)
    if unique_days[0] not in (today, yesterday):
        return 0
    streak = 1
    for i in range(1, len(unique_days)):
        if unique_days[i] == unique_days[i - 1] - timedelta(days=1):
            streak += 1
        else:
            break
    return streak


def get_user_stats(session, user_id):
    df = get_logs_df(session, user_id)
    if df is None or df.empty:
        return {
            "total_pages": 0, "total_minutes": 0,
            "current_streak": 0, "best_day_pages": 0,
            "best_day_minutes": 0, "total_days": 0,
        }
    total_pages      = int(df["pages_read"].sum())
    total_minutes    = int(df["minutes_spent"].sum())
    streak           = current_streak(df)
    total_days       = df["log_date"].nunique()
    dp               = df.groupby("log_date")["pages_read"].sum()
    dm               = df.groupby("log_date")["minutes_spent"].sum()
    best_day_pages   = int(dp.max()) if not dp.empty else 0
    best_day_minutes = int(dm.max()) if not dm.empty else 0
    return {
        "total_pages": total_pages, "total_minutes": total_minutes,
        "current_streak": streak, "best_day_pages": best_day_pages,
        "best_day_minutes": best_day_minutes, "total_days": total_days,
    }


def get_user_level(total_pages):
    try:
        from utils.db import get_session
        s = get_session()
        lvl = (
            s.query(LevelDefinition)
            .filter(LevelDefinition.min_pages <= total_pages)
            .order_by(LevelDefinition.min_pages.desc())
            .first()
        )
        if lvl:
            s.expunge(lvl)
        s.close()
        return lvl
    except Exception:
        return None


def get_next_level(total_pages):
    try:
        from utils.db import get_session
        s = get_session()
        nxt = (
            s.query(LevelDefinition)
            .filter(LevelDefinition.min_pages > total_pages)
            .order_by(LevelDefinition.min_pages.asc())
            .first()
        )
        if nxt:
            s.expunge(nxt)
        s.close()
        return nxt
    except Exception:
        return None

def get_level_info(session, total_pages):
    current = (
        session.query(LevelDefinition)
        .filter(LevelDefinition.min_pages <= total_pages)
        .order_by(LevelDefinition.min_pages.desc())
        .first()
    )
    nxt = (
        session.query(LevelDefinition)
        .filter(LevelDefinition.min_pages > total_pages)
        .order_by(LevelDefinition.min_pages.asc())
        .first()
    )
    pages_to_next = (nxt.min_pages - total_pages) if nxt else 0
    return current, nxt, pages_to_next


def get_user_badges(session, user_id):
    try:
        return (
            session.query(UserBadge)
            .filter(UserBadge.user_id == user_id)
            .all()
        )
    except Exception:
        return []


def get_user_books(session, user_id):
    try:
        from utils.models import Book, UserBook
        return (
            session.query(Book)
            .join(UserBook, UserBook.book_id == Book.id)
            .filter(
                UserBook.user_id == user_id,
                UserBook.is_active == True
            )
            .all()
        )
    except Exception:
        return []