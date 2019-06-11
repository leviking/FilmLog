""" Project interactions for API """

from flask import jsonify, request, make_response, url_for
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
            "type" : "projects",
            "id" : str(binderID) + ":" + str(row['projectID']),
            "attributes" : {
                "name" : row['name'],
                "film_count" : row['filmCount'],
                "created_on" : row['createdOn'],
                "composite_id" : {
                    "binder_id" : str(binderID),
                    "project_id": str(row['projectID']),
                }
            },
            "links" : {
                "self" : url_for("api.project_details",
                                 binderID=binderID,
                                 projectID=row['projectID'])
            }
        }
        projects['data'].append(project)
    return jsonify(projects), status.HTTP_200_OK

def get(connection, binderID, projectID):
    """ Get specific project """
    userID = current_user.get_id()
    qry = text("""SELECT projectID, name, filmCount, createdOn FROM Projects
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
            "id" : str(binderID) + ":" + str(projectID),
            "attributes" : {
                "name" : projects_query['name'],
                "film_count" : projects_query['filmCount'],
                "created_on" : projects_query['createdOn'],
                "composite_id" : {
                    "binder_id" : str(binderID),
                    "project_id": str(projectID),
                }
            },
            "links" : {
                "self" : url_for("api.project_details",
                                 binderID=binderID,
                                 projectID=projectID)
            }
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
                           name=json['data']['attributes']['name'])
    except IntegrityError:
        return "FAILED", status.HTTP_409_CONFLICT
    location_url = url_for('api.project_details',
                           binderID=binderID,
                           projectID=nextProjectID)
    json['data']['id'] = str(binderID) + ":" + str(nextProjectID)
    json['data']['attributes']['film_count'] = str(0)
    json['data']['links'] = {
        "self" : location_url
    }
    resp = make_response(jsonify(json))
    resp.headers['Location'] = location_url
    return resp, status.HTTP_201_CREATED
