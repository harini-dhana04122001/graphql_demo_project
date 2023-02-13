from flask import Blueprint, request, Response

from user.service import create_user_details

display = Blueprint('display', __name__)


@display.route('/', methods=['POST'])
def create_user_detail():
    user_data = request.get_json()
    username = user_data['username']
    email = user_data['email']
    create_user_details(username, email)
    return Response('successfully created')
