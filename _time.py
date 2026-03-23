from datetime import datetime, timezone

def today_str_utc() -> str:
    return datetime.now(timezone.utc).date().isoformat()

def approx_tokens_for_text(text: str) -> int:
    if not text:
        return 0
    return (len(text) + 3) // 4


def ensure_today_bucket(uid: int, user_daily_tokens: dict) -> dict:
    today = today_str_utc()
    bucket = user_daily_tokens.get(uid)
    if not bucket or bucket.get('date') != today:
        user_daily_tokens[uid] = {'date': today, 'used': 0}
    return user_daily_tokens[uid]

def get_used_today(uid: int, user_daily_tokens: dict) -> int:
    return ensure_today_bucket(uid, user_daily_tokens)['used']

def add_used_today(uid: int, delta_tokens: int, user_daily_tokens: dict) -> int:
    bucket = ensure_today_bucket(uid, user_daily_tokens)
    bucket['used'] = int(bucket.get('used', 0) + max(0, int(delta_tokens)))
    return bucket['used']

def get_resp_total_tokens(resp):
    try:
        u = getattr(resp, "usage", None)
        if not u:
            return None
        total = getattr(u, "total_tokens", None)
        if total is not None:
            return int(total)
        pt = getattr(u, "prompt_tokens", None)
        ct = getattr(u, "completion_tokens", None)
        if pt is not None or ct is not None:
            return int((pt or 0) + (ct or 0))
    except Exception:
        pass
    return None


