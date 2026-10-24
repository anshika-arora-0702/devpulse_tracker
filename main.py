from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, status, Depends
from database import Engine
from exceptions.url_exceptions import InvalidHttpsUrl
from sqlalchemy.exc import SQLAlchemyError
import requests

from service.discourse_client import DiscourseClientService
from service.normalize_topics import TopicNormalizeService
from service.reporter import ReporterService
from service.triage import TriageService
from service.slack_notifier import SlackNotifier
from storage import createStorage
from storage import Storage

import json
from pathlib import Path

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "https://meta.discourse.org/"
CONFIG_PATH = Path(__file__).resolve().parent / "config" / "config1.json"

def load_config() -> dict:
    with CONFIG_PATH.open(encoding="utf-8") as config_file:
        return json.load(config_file)

config = load_config()
config["base_url"] = config.get("base_url") or DEFAULT_BASE_URL

discourse_client = DiscourseClientService()
topic_normalizer = TopicNormalizeService()
reporter = ReporterService()
triage = TriageService()
slack_notifier = SlackNotifier()

app = FastAPI()

from storage import Base
Base.metadata.create_all(bind=Engine)

@app.post("/")
def get_topics(data : str | None = None, storage : Storage = Depends(createStorage)):

    base_url = data or config["base_url"]

    try:
        all_topics_summary_list = discourse_client.get_latest_topics(base_url)
        result = []

        for summary in all_topics_summary_list :
            detail = discourse_client.get_topic_details(base_url,int(summary["id"]))
            result.append(topic_normalizer.normalize_topic(summary, detail, {**config, "base_url": base_url}))

    except InvalidHttpsUrl as error:
        logger.warning("Rejected invalid Discourse URL")
        raise HTTPException(status_code=400, detail=str(error)) from error

    except requests.exceptions.Timeout as error:
        logger.exception("Discourse request timed out")
        raise HTTPException(status_code=504, detail="Discourse timed out") from error

    except requests.exceptions.RequestException as error:
        logger.exception("Discourse request failed")
        raise HTTPException( status_code=502, detail="Could not retrieve data from Discourse") from error


    for normalized_topic in result :

        normalized_topic["status"] = triage.classify_topic_status(normalized_topic,24,72)

        normalized_topic["priority"] = {
            "UNANSWERED": "HIGH",
            "FOLLOW_UP": "MEDIUM",
            "NEEDS_REVIEW": "MEDIUM",
            "ACTIVE": "LOW"
        }.get(normalized_topic["status"], "NONE")

    sorted_topics = triage.sort_topics(result)

    try:
        alerts_list = storage.insert_topics_and_get_alerts_list(sorted_topics) or []

    except SQLAlchemyError as error:
        logger.exception("Failed to save topics")
        raise HTTPException(status_code=500, detail="Database operation failed") from error
    
    for topic in alerts_list:
        message = f"*{topic['status']}* — <{topic['url']}|{topic['title']}>"

        try:
            slack_notifier.send_slack_message(message)

        except ValueError as error:
            logger.error("Slack webhook is not configured")
            raise HTTPException(status_code=500, detail="Slack notifications are not configured") from error

        except requests.exceptions.RequestException as error:
            logger.exception("Failed to send Slack alert")
            raise HTTPException(status_code=502, detail="Could not send Slack alert") from error

        except RuntimeError as error:
            logger.error("Slack rejected the alert: %s", error)
            raise HTTPException(status_code=502, detail="Slack did not accept the alert") from error

        try:
            storage.mark_alert(topic["id"], topic["status"])

        except SQLAlchemyError as error:
            logger.exception("Slack alert sent, but failed to save alert history")
            raise HTTPException(status_code=500, detail="Alert sent, but alert history could not be saved") from error

    reporter.write_csv(sorted_topics,r"C:\Users\anshi\Downloads\report.csv")
    print(reporter.count_topics_by_status(sorted_topics))
    return sorted_topics




