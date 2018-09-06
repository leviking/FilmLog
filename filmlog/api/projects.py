from flask_login import LoginManager, login_required, current_user, login_user, UserMixin
from flask import Blueprint, jsonify, request, make_response
from sqlalchemy.sql import select, text, func
from sqlalchemy.exc import IntegrityError
from filmlog import database, functions
from flask_api import status
from filmlog import engine
from filmlog.functions import next_id

## Projects
def get_all(connection, transaction, binderID):
    userID = current_user.get_id()
    qry = text("""SELECT projectID, name, filmCount, createdOn FROM Projects
        WHERE binderID = :binderID
        AND userID = :userID
        ORDER BY createdOn""")
    projects_query = connection.execute(qry, binderID=binderID, userID = userID).fetchall()
    projects = {
        "data": []
    }
    for row in projects_query:
        project = {
            "type" : "projects",
            "id" : {
                "binder_id" : str(binderID),
                "project_id": str(row['projectID']),
            },
            "attributes" : {
                "name" : row['name'],
                "film_count" : row['filmCount'],
                "created_on" : row['createdOn']
            }
        }
        projects["data"].append(project)
    return jsonify(projects), status.HTTP_200_OK
