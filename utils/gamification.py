from datetime import date, timedelta

LEVELS = [
    (0,    "📖 Bookworm Beginner",  0),
    (100,  "🐛 Eager Reader",       100),
    (300,  "🦋 Story Explorer",     300),
    (600,  "🌟 Page Turner",        600),
    (1000, "🚀 Reading Rocket",     1000),
    (1500, "🏆 Literary Champion",  1500),
    (2500, "👑 Master Reader",      2500),
]

BADGES = {
    "first_log":      {"name": "First Step 🐾",    "desc": "Logged your first reading session!"},
    "7_day_streak":   {"name": "Week Warrior 🔥",   "desc": "Read 7 days in a row!"},
    "30_day_streak":  {"name": "Monthly Master 🌙", "desc": "Read 30 days in a row!"},
    "100_pages":      {"name": "Century Club 💯",   "desc": "Read 100 pages total!"},
    "1000_pages":     {"name": "Thousand Pages 📚", "desc": "Read 1000 pages total!"},
    "5_books":        {"name": "Five Books 🖐",      "desc": "Completed 5 books!"},
    "10_books":       {"name": "Bookshelf Builder 🏗", "desc": "Completed 10 books!"},
}

def get_level(total_pages: int) -> dict:
    current_level_name = LEVELS[0][1]
    current_threshold = 0
    next_threshold = LEVELS[1][0]
    next_level_name = LEVELS[1][1]

    for i, (threshold, name, _) in enumerate(LEVELS):
        if total_pages >= threshold:
            current_level_name = name
            current_threshold = threshold
            if i + 1 < len(LEVELS):
                next_threshold = LEVELS[i + 1][0]
                next_level_name = LEVELS[i + 1][1]
            else:
                next_threshold = None
                next_level_name = None

    pages_in_level = total_pages - current_threshold
    pages_to_next = (next_threshold - total_pages) if next_threshold else 0

    return {
        "level_name": current_level_name,
        "pages_in_level": pages_in_level,
        "pages_to_next": pages_to_next,
        "next_level_name": next_level_name,
        "total_pages": total_pages,
        "is_max_level": next_threshold is None,
    }

def calculate_streak(log_dates: list) -> int:
    if not log_dates:
        return 0
    unique_dates = sorted(set(log_dates), reverse=True)
    streak = 0
    today = date.today()
    check_date = today
    for d in unique_dates:
        if d == check_date or d == check_date - timedelta(days=1):
            streak += 1
            check_date = d
        else:
            break
    return streak

def check_badges(stats: dict, log_dates: list, existing_badges: list) -> list:
    """Returns list of new badge keys earned."""
    new_badges = []
    existing = set(existing_badges)

    if stats["total_logs"] >= 1 and "first_log" not in existing:
        new_badges.append("first_log")

    streak = calculate_streak(log_dates)
    if streak >= 7 and "7_day_streak" not in existing:
        new_badges.append("7_day_streak")
    if streak >= 30 and "30_day_streak" not in existing:
        new_badges.append("30_day_streak")

    if stats["total_pages"] >= 100 and "100_pages" not in existing:
        new_badges.append("100_pages")
    if stats["total_pages"] >= 1000 and "1000_pages" not in existing:
        new_badges.append("1000_pages")

    if stats["books_completed"] >= 5 and "5_books" not in existing:
        new_badges.append("5_books")
    if stats["books_completed"] >= 10 and "10_books" not in existing:
        new_badges.append("10_books")

    return new_badges

def get_level_greeting(level_name: str, name: str) -> str:
    greetings = {
        "📖 Bookworm Beginner": f"Welcome, {name}! Every great reader starts somewhere. Let's begin your journey!",
        "🐛 Eager Reader": f"Great going, {name}! You're developing a wonderful reading habit!",
        "🦋 Story Explorer": f"Wow, {name}! You're exploring so many amazing stories. Keep it up!",
        "🌟 Page Turner": f"Impressive, {name}! You can't put books down — and that's a superpower!",
        "🚀 Reading Rocket": f"You're on fire, {name}! Blasting through books like a true reading rocket!",
        "🏆 Literary Champion": f"Champion-level reading, {name}! You inspire everyone around you!",
        "👑 Master Reader": f"All hail {name}, the Master Reader! You've conquered the reading world!",
    }
    return greetings.get(level_name, f"Hello, {name}! Keep reading!")