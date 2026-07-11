from __future__ import annotations

from ke.models.feedback import QueryFeedback


class FeedbackValidator:
    MAX_COMMENT_LENGTH = 2000
    SPAM_PATTERNS: list[str] = [
        "http://", "https://", "www.", "buy now", "click here", "free money",
    ]

    def is_valid(self, feedback: QueryFeedback) -> bool:
        if feedback.rating is not None and (feedback.rating < 1 or feedback.rating > 5):
            return False
        if feedback.flag and feedback.flag not in ("spam", "incorrect", "offensive", "other"):
            return False
        if len(feedback.comment) > self.MAX_COMMENT_LENGTH:
            return False
        comment_lower = feedback.comment.lower()
        if any(p in comment_lower for p in self.SPAM_PATTERNS):
            return False
        return True

    def deduplicate(self, items: list[dict]) -> list[dict]:
        seen: set[str] = set()
        deduped: list[dict] = []
        for item in items:
            key = f"{item.get('query_id','')}:{item.get('user_id','')}"
            if key not in seen:
                seen.add(key)
                deduped.append(item)
        return deduped
