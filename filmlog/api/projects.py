""" Project interactions for API """
import datetime
from flask import jsonify, request, make_response
from flask_api import status
from flask_login import current_user
from sqlalchemy.sql import text
from sqlalchemy.exc import IntegrityError

from filmlog.functions import next_id

## Projects
def get_all(connection, binderID):
    """ Get all projects """
    userID = current_user.get_id()
    qry = text("""SELECT projectID, name, filmCount, createdOn FROM Projects
        WHERE binderID = :binderID
        AND userID = :userID
        ORDER BY createdOn""")
    projects_query = connection.execute(qry,
                                        binderID=binderID,
                                        userID=userID).fetchall()
    projects = {
        "data": []
    }
    for row in projects_query:
        project = {
            "id" : str(row['projectID']),
            "name" : row['name'],
            "film_count" : row['filmCount'],
            "created_on" : row['createdOn'],
            "composite_id" : {
                "binder_id" : binderID,
                "project_id": row['projectID'],
            }
        }
        projects['data'].append(project)
    return jsonify(projects), status.HTTP_200_OK

def get(connection, binderID, projectID):
    """ Get specific project """
    userID = current_user.get_id()
    qry = text("""SELECT projectID, name, filmCount, createdOn, notes
        FROM Projects
        WHERE binderID = :binderID
        AND projectID = :projectID
        AND userID = :userID
        ORDER BY createdOn""")
    projects_query = connection.execute(qry,
                                        binderID=binderID,
                                        projectID=projectID,
                                        userID=userID).fetchone()
    projects = {
        "data": {
            "type" : "projects",
            "id" : projectID,
            "binderID" : binderID,
            "name" : projects_query['name'],
            "notes" : projects_query['notes'],
            "film_count" : projects_query['filmCount'],
            "created_on" : projects_query['createdOn'],
        }
    }
    return jsonify(projects), status.HTTP_200_OK

def post(connection, binderID):
    """ Insert new project """
    userID = current_user.get_id()
    json = request.get_json()
    nextProjectID = next_id(connection, 'projectID', 'Projects')
    qry = text("""INSERT INTO Projects
        (projectID, binderID, userID, name)
        VALUES (:projectID, :binderID, :userID, :name)""")
    try:
        connection.execute(qry,
                           projectID=nextProjectID,
                           binderID=binderID,
                           userID=userID,
                           name=json['data']['name'])
    except IntegrityError:
        return "FAILED", status.HTTP_409_CONFLICT
    json['data']['id'] = str(nextProjectID)
    json['data']['film_count'] = str(0)
    json['data']['created_on'] = datetime.datetime.now()
    resp = make_response(jsonify(json))
    return resp, status.HTTP_201_CREATED

def delete(connection, binderID, projectID):
    """ Delete a project """
    userID = current_user.get_id()
    qry = text("""DELETE FROM Projects
        WHERE userID = :userID
        AND binderID = :binderID
        AND projectID = :projectID""")
    try:
        connection.execute(qry,
                           userID=userID,
                           binderID=binderID,
                           projectID=projectID)
    except IntegrityError:
        return "FAILED", status.HTTP_403_FORBIDDEN
    return "OK", status.HTTP_204_NO_CONTENT
