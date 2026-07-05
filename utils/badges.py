from utils.models import UserBadge, BadgeDefinition
from datetime import datetime


def award_badges(session, user, df):
    """
    Check all badge conditions and award any newly earned badges.
    user is a SQLAlchemy User ORM object — use user.id not user["id"]
    """
    if df is None or df.empty:
        return

    # ── Current stats ────────────────────────────────────────────────────────
    total_pages   = int(df["pages_read"].sum())   if not df.empty else 0
    total_minutes = int(df["minutes_spent"].sum()) if not df.empty else 0
    total_days    = df["log_date"].nunique()        if not df.empty else 0

    # Streak calculation
    import pandas as pd
    from datetime import date, timedelta
    streak = 0
    if not df.empty:
        today = date.today()
        log_dates = sorted(
            df["log_date"].unique(), reverse=True)
        for i, d in enumerate(log_dates):
            expected = today - timedelta(days=i)
            if pd.Timestamp(d).date() == expected:
                streak += 1
            else:
                break

    # Books completed (read at least once with pages > 0)
    books_read = df["book_id"].nunique() if not df.empty else 0

    # ── Already owned badge IDs ───────────────────────────────────────────────
    # FIX: use user.id not user["id"]
    owned = {
        x.badge_id
        for x in session.query(UserBadge)
        .filter(UserBadge.user_id == user.id)
        .all()
    }

    # ── All badge definitions ─────────────────────────────────────────────────
    all_badges = session.query(BadgeDefinition).all()

    # ── Check each badge condition ────────────────────────────────────────────
    newly_earned = []
    for badge in all_badges:
        if badge.id in owned:
            continue  # already has this badge

        earned = False

        if badge.metric_type == "pages":
            earned = total_pages >= badge.threshold

        elif badge.metric_type == "minutes":
            earned = total_minutes >= badge.threshold

        elif badge.metric_type == "streak":
            earned = streak >= badge.threshold

        elif badge.metric_type == "books":
            earned = books_read >= badge.threshold

        elif badge.metric_type == "days":
            earned = total_days >= badge.threshold

        if earned:
            new_badge = UserBadge(
                user_id=user.id,      # FIX: user.id not user["id"]
                badge_id=badge.id,
                earned_at=datetime.utcnow(),
            )
            session.add(new_badge)
            newly_earned.append(badge.name)

    if newly_earned:
        session.commit()

    return newly_earned