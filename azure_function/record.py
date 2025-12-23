from datetime import datetime

class Record:
    def __init__(
        self,
        user_id: str,
        note: str,
        version: int,
        decision: bool,
        updated_at: datetime,
    ):
        self.user_id = user_id
        self.note = note
        self.version = version
        self.decision = decision
        self.updated_at = updated_at
