import logging

from dotenv import load_dotenv
load_dotenv()

import os
from flask import Flask, request
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler

from sqlalchemy import (
    create_engine,
    select,
)
from sqlalchemy.orm import (
    Session,
)

from models import (
    Knowledge,
    Base,
)

basedir = os.path.abspath(os.path.dirname(__file__))
flask_app = Flask(__name__)
flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
engine = create_engine("sqlite:///slack_app.db", echo=True)


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = App(logger=logger)
handler = SlackRequestHandler(app)

# TODO: try except for checking if acronym is present in db
def get_knowledge_description(title: str) -> str:
    with Session(engine) as session:
        # TODO: search through 
        stmt = select(Knowledge.description).where(Knowledge.title == title)
        acronym_description = session.scalar(stmt)
        return acronym_description

# TODO: try except for adding the acronym (return True is ok, else False)
def add_knowledge(title: str, description: str):
    with Session(engine) as session:
        new_knowledge = Knowledge(
            title=title,
            description=description
        )
        session.add(new_knowledge)
        session.commit()
        return True


def list_knowledge():
    with Session(engine) as session:
        stmt = select(Knowledge.title)
        knowledge_list = session.scalars(stmt)
        return knowledge_list
    

@app.event("app_home_opened")
def handle_command(say):
    say("Hey there!")


@app.command("/remember")
def remember_command(ack, respond, command):
    ack()
    text = command['text'].split()
    title = text[0]
    description = ' '.join(text[1:])
    add_knowledge(title=title, description=description)
    respond(f"Knowledge: {title} is saved")


@app.command("/what")
def what_command(ack, respond, command):
    ack()
    text = command['text'].split()
    acronym = text[0]
    acronym_description = get_knowledge_description(title=acronym)
    respond(acronym_description)

# TODO: list as bullet points: acronym: description
@app.command("/list")
def list_command(ack, respond, command):
    ack()
    acronym_list = list_knowledge()
    acronyms = '; '.join(acronym_list)
    respond(f"List of saved acronyms: {acronyms}")

@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)


if __name__ == "__main__":
    Base.metadata.create_all(engine)
    flask_app.run(debug=True, port=3000)


# pip install -r requirements.txt

# # -- OAuth flow -- #
# export SLACK_SIGNING_SECRET=***
# export SLACK_BOT_TOKEN=xoxb-***
# export SLACK_CLIENT_ID=111.111
# export SLACK_CLIENT_SECRET=***
# export SLACK_SCOPES=app_mentions:read,chat:write

# FLASK_APP=oauth_app.py FLASK_ENV=development flask run -p 3000
