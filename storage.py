from fastapi import Depends
from datetime import datetime, timezone, timedelta
from sqlalchemy import Column, String, Integer,  DateTime, Boolean
from sqlalchemy.orm import declarative_base
from database import SessionLocal

Base = declarative_base()

ACTIONABLE = {"UNANSWERED", "FOLLOW_UP", "NEEDS_REVIEW"}


def get_db():
    db = SessionLocal()
    try:
        yield db

    finally:
        db.close()

class Topic(Base):

    __tablename__ = "topics"

    id = Column(
        Integer,
        nullable=False,
        primary_key=True
    )

    title =  Column(
        String, 
        nullable=False
    )

    url =  Column(
        String, 
        nullable=False
    )

    category =  Column(
        String, 
        nullable=False
    )

    status =  Column(
        String, 
        nullable=False
    )

    priority =  Column(
        String, 
        nullable=False
    )   

    solved = Column(
        Boolean,
        nullable=True
    )


    last_alerted_status = Column(
        String,
        nullable=True
    )

    last_status_change_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    last_alerted_at =Column (
        DateTime(timezone=True),
        nullable=True
    ) 

class Storage:

    def __init__(self, db_session):
        self.db_session = db_session

    def update(self, topic):

        existing_topic = self.db_session.get(Topic, topic["id"])

        if existing_topic.status != topic["status"]:
            existing_topic.last_status_change_at = datetime.now(timezone.utc)

        existing_topic.title = topic["title"]
        existing_topic.url = topic["url"]
        existing_topic.category = topic["category"]
        existing_topic.status = topic["status"]
        existing_topic.priority = topic["priority"]
        existing_topic.solved = topic["solved"]

    def insert_topics_and_get_alerts_list(self, topics:list[dict]):

        alert_candidates = []

        if not topics:
            return []

        with self.db_session.begin():
        
            for topic in topics:

                existing_topic = self.db_session.get(Topic, topic["id"])

                if self.should_alert(topic, existing_topic):
                    alert_candidates.append(topic.copy())


                if existing_topic is None:

                    topic_db = Topic(    
                        id = topic["id"],
                        title = topic["title"],
                        url= topic["url"],
                        category= topic["category"],
                        status = topic["status"],
                        priority = topic["priority"],
                        solved =  topic["solved"],
                        last_status_change_at = datetime.now(timezone.utc),
                        )

                    self.db_session.add(topic_db)

                else:
                    self.update(topic)

        return alert_candidates

    def should_alert(self, topic, existing_topic):

        if topic["status"] not in ACTIONABLE:
            return False

        if existing_topic is None:
            return True

        if existing_topic.last_alerted_at is None:
            return True

        if existing_topic.last_alerted_status != topic["status"]:
            return True

        now = datetime.now(timezone.utc)

        if  now - existing_topic.last_alerted_at >= timedelta(hours = 24):
            return True

        return False

    def mark_alert(self, topic_id, topic_status):

        with self.db_session.begin():
            topic = self.db_session.get(Topic, topic_id)

            if topic is None:
                raise LookupError(f"Topic {topic_id} disappeared before alert history was saved")

            topic.last_alerted_status = topic_status
            topic.last_alerted_at = datetime.now(timezone.utc)

def createStorage(db = Depends(get_db)) -> Storage:
    return Storage(db)