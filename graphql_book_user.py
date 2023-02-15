import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField

from building.model import Building
from floor.model import Floor
# from book.model import Book
# from user.model import User
from service import create_details
from community.model import Community


class CommunityObject(SQLAlchemyObjectType):
    class Meta:
        model = Community
        interfaces = (graphene.relay.Node,)


class BuildingObject(SQLAlchemyObjectType):
    class Meta:
        model = Building
        interfaces = (graphene.relay.Node,)


class FloorObject(SQLAlchemyObjectType):
    class Meta:
        model = Floor
        interfaces = (graphene.relay.Node,)
# class BookObject(SQLAlchemyObjectType):
#     class Meta:
#         model = Book
#         interfaces = (graphene.relay.Node,)
#
#
# class UserObject(SQLAlchemyObjectType):
#     class Meta:
#         model = User
#         interfaces = (graphene.relay.Node,)


class Query(graphene.ObjectType):
    node = graphene.relay.Node.Field()
    all_communitys = SQLAlchemyConnectionField(CommunityObject)
    all_buildings = SQLAlchemyConnectionField(BuildingObject)
    all_floors = SQLAlchemyConnectionField(FloorObject)
    # all_books = SQLAlchemyConnectionField(BookObject)
    # all_users = SQLAlchemyConnectionField(UserObject)


class AddCommunity(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        agent_name = graphene.String(required=True)
        agent_contact = graphene.String(required=True)
    community = graphene.Field(lambda: CommunityObject)

    def mutate(self, info, name, agent_name, agent_contact):
        community = Community(name, agent_name, agent_contact)
        # if user is not None:
        #     book.author_id = user.id
        create_details(community)
        return AddCommunity(community=community)


class AddBuilding(graphene.Mutation):
    class Arguments:
        block_name = graphene.String(required=True)
        name = graphene.String(required=True)
        agent_name = graphene.String(required=True)
    building = graphene.Field(lambda: BuildingObject)

    def mutate(self, info, block_name, agent_name, name):
        community = Community.query.filter_by(name=name, agent_name=agent_name).first()
        building = Building(block_name, community.id)
        create_details(building)
        return AddBuilding(building=building)


class AddFloor(graphene.Mutation):
    class Arguments:
        floor_name = graphene.String(required=True)
        block_name = graphene.String(required=True)
    floor = graphene.Field(lambda: FloorObject)

    def mutate(self, info, block_name, floor_name):
        building = Building.query.filter_by(block_name=block_name).first()
        floor = Floor(floor_name, building.id)
        create_details(floor)
        return AddFloor(floor=floor)

# class AddBook(graphene.Mutation):
#     class Arguments:
#         title = graphene.String(required=True)
#         description = graphene.String(required=True)
#         year = graphene.Int(required=True)
#         username = graphene.String(required=True)
#     book = graphene.Field(lambda: BookObject)
#
#     def mutate(self, info, title, description, year, username):
#         user = User.query.filter_by(username=username).first()
#         book = Book(title, description, year, user.id)
#         # if user is not None:
#         #     book.author_id = user.id
#         create_details(book)
#         return AddBook(book=book)
#
#
# class AddUser(graphene.Mutation):
#     class Arguments:
#         username = graphene.String(required=True)
#         email = graphene.String(required=True)
#     user = graphene.Field(lambda: UserObject)
#
#     def mutate(self, info, username, email):
#         user = User(username, email)
#         # if user is not None:
#         #     book.author_id = user.id
#         create_details(user)
#         return AddUser(user=user)


class Mutation(graphene.ObjectType):
    # add_book = AddBook.Field()
    # add_user = AddUser.Field()
    add_community = AddCommunity.Field()
    add_building = AddBuilding.Field()
    add_floor = AddFloor.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
