from datetime import datetime

class TopicNormalizeService():

    def normalize_topic(self, topic_summary: dict, topic_detail: dict, config:dict ):

            posts_data = topic_detail.get("post_stream", {})
            posts = posts_data.get("posts", [])
            ids = posts_data.get("stream", [])
            complete = len(ids) == len(posts)

            bot_names = {name.casefold() for name in config.get("bot_usernames", [])}
            human_replies = None
            bot_replies = None

            if complete:
                replies = [p for p in posts if p.get("post_number", 0) > 1]
                bot_replies = sum((p.get("username") or "").casefold() in bot_names for p in replies)
                human_replies = len(replies) - bot_replies

            solved_field = config.get("solved_field")
            solved_value = config.get("solved_value", True)
            solved = None

            if solved_field:
                for source in (topic_detail, topic_summary):
                    if solved_field in source:
                        if source[solved_field] == solved_value:
                            solved = True
                            break
                        elif source[solved_field] is not None:
                            solved = False

            tags = {str(t).casefold() for t in topic_summary.get("tags", [])}
            excluded_tags = {t.casefold() for t in config.get("excluded_tags", [])}

            allowed_categories = set(config.get("support_category_ids", []))

            if allowed_categories:
                is_question = topic_summary.get("category_id") in allowed_categories

            else:
                is_question = True

            if tags & excluded_tags:
                is_question = False

            created = datetime.fromisoformat(topic_summary["created_at"])

            last_posted = datetime.fromisoformat(
                topic_summary.get("last_posted_at") or topic_summary["created_at"]
            )

            return {
                "id": int(topic_summary["id"]),
                "title": topic_summary.get("title") or "(untitled)",
                "url": f"{config['base_url'].rstrip('/')}/t/{int(topic_summary['id'])}",
                "category": str(topic_summary.get("category_id", "unknown")),
                "is_question": is_question,
                "created_at": created,
                "last_posted_at": last_posted,
                "human_reply_count": human_replies,
                "bot_reply_count": bot_replies,
                "solved": solved,
            }



            
