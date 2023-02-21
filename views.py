from flask import Blueprint
from flask_graphql import GraphQLView

from schema import schema

display = Blueprint('display', __name__)

display.add_url_rule(
    '/graphql-api',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=True  # for having the GraphiQL interface
    )
)


# @display.route('/get',methods=['GET'])
# def get_community():
#     communities = Community.query.all()
#     community = [community.id for community in communities]
#     building = Building.query.filter_by(community_id.in_(community)).all()
#     print(list(building.block_name))
#     # return jsonify(dict(building))

# @display.route('/', methods=['POST'])
# def create_book_detail():
#     book_data = request.get_json()
#     title = book_data['title']
#     description = book_data['description']
#     year = book_data['year']
#     author_id = book_data['author_id']
#     create_details(title, description, year, author_id)
#     return Response('successfully created')
