
# Universal TTRPG Organizer

A web application that allows users to create groups as the “Game Master” and invite other accounts as “players”. A player can create characters which can be later added to a group they are an invited participant of. A group “homepage” will be generated that takes the most important character and game information and summarizes it for easy reference, while also allowing users to see full versions of character sheets. We will also allow connection between players to a group hosted by the GM and will allow players to create character information sheets and also summarize the important information to a page that everyone sees/shares.


## Tech Stack

**Client:** Flask

**Server:** SQLAlchemy


## Run Locally

Clone the project

```bash
  git clone https://github.com/ttrpg-web-app/website.git
```

Go to the project directory

```bash
  cd ttrpg-site
```

Create environment
```bash
python3 -m venv .venv
. .venv/bin/activate
```

Install dependencies (use either that works for you!)
```bash
pip install Flask
pip install SQLAlchemy
pip install -U Flask-SQLAlchemy
pip install flask-login
```
```bash
python3 -m pip install Flask
python3 -m pip install SQLAlchemy
python3 -m pip install -U Flask-SQLAlchemy
python3 -m pip install flask-login
```

Launch localhost
```bash
python3 app.py
```
[Finally, visit this page to view.](localhost:5000)

## Authors

- [@luke-danger](https://github.com/luke-danger)
- [@wheatleyinabox](https://github.com/wheatleyinabox)
- [@ragod02](https://github.com/ragod02)
- [@Reveling-h](https://github.com/Reveling-h)
- [@plexin123](https://github.com/plexin123)
