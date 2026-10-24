from datetime import datetime, timezone

PRIORITY = {
    "UNANSWERED": 1,
    "FOLLOW_UP": 2,
    "NEEDS_REVIEW": 3,
    "ACTIVE": 4,
    "SOLVED": 5,
    "EXCLUDED": 6,
}



class TriageService():

    def __init__(self):
        pass

    def classify_topic_status(self, topic: dict, unanswered_hours=24, followup_hours=72) -> str:
        now = datetime.now(timezone.utc)

        if not topic.get("is_question", False):
            return "EXCLUDED"
        
        if topic.get("solved") is True:
            return "SOLVED"

        human_replies = topic["human_reply_count"]

        age_hours = (now - topic["created_at"]).total_seconds() / 3600
        if human_replies == 0 and age_hours >= unanswered_hours:
            return "UNANSWERED"

        idle_hours = (now - topic["last_posted_at"]).total_seconds() / 3600
        if idle_hours >= followup_hours:
            return "FOLLOW_UP"

        if idle_hours < followup_hours:
            return "ACTIVE"

        return "NEEDS_REVIEW"

    def sort_topics(self, topics: list[dict]) -> list[dict]:
        return sorted(topics, key=lambda t: (
            PRIORITY[t["status"]], t["created_at"], t["id"]
        ))

 

    