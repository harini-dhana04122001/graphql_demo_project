import graphene
from flask_graphql_auth import AuthInfoField, create_refresh_token, create_access_token, query_header_jwt_required, \
    mutation_jwt_refresh_token_required, get_jwt_identity
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from sqlalchemy.orm import load_only

from building.model import Building
from floor.model import Floor
from permission.model import Permission, PermissionField
from service import create_details, update_details
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


class ProtectedCommunity(graphene.Union):
    class Meta:
        types = (CommunityObject, AuthInfoField)


class CommunityObjectTuple(graphene.ObjectType):
    name = graphene.String()
    agent_name = graphene.String()
    agent_contact = graphene.Int()

    @classmethod
    def from_tuples(cls, data):
        if data[0] is not None:
            name_data = data[0]
        else:
            name_data = None
        if data[1]:
            agent_name_data = data[1]
        else:
            agent_name_data = None
        if data[2]:
            contact_data = data[1]
        else:
            contact_data = None
        return cls(
            name=name_data,
            agent_name=agent_name_data,
            agent_contact=contact_data
        )


class Query(graphene.ObjectType):
    node = graphene.relay.Node.Field()
    all_community = SQLAlchemyConnectionField(CommunityObject)
    all_buildings = SQLAlchemyConnectionField(BuildingObject)
    all_floors = SQLAlchemyConnectionField(FloorObject)
    get_community = graphene.List(ProtectedCommunity, token=graphene.String())
    get_community_by_name = graphene.Field(ProtectedCommunity, token=graphene.String(), name=graphene.String())
    community_with_auth = graphene.List(CommunityObjectTuple, username=graphene.String())

    def resolve_community_with_auth(self, info, username):
        permission = Permission.query.filter_by(username=username).first()
        permission_field = PermissionField.query.filter_by(permission_id=permission.id).all()
        empty_list = []
        for i in permission_field:
            if i.model == 'Community' and i.access_type == 'read':
                empty_list.append(i.field)
                # elif i.model == 'Building' and i.access_type == 'read':
                #     empty_list.append(i.field)
                #     query = BuildingObject.get_query(info)
                # elif i.model == 'Floor' and i.access_type == 'read':
                #     empty_list.append(i.field)
                #     query = FloorObject.get_query(info)
        query = CommunityObject.get_query(info)
        result = query.options(load_only('name','agent_name')).all()
        print(result)
        # print(type(result[0]))
        final_output = [CommunityObjectTuple.from_tuples(community) for community in result]
        return final_output

    @query_header_jwt_required
    def resolve_get_community(self, info):
        print(info.context)
        query = CommunityObject.get_query(info)
        print(query)
        result = query.all()
        print(result)
        print(type(result))
        return result

    @query_header_jwt_required
    def resolve_get_community_by_name(self, info, name):
        query = CommunityObject.get_query(info)
        result = query.filter(Community.name.contains(name)).first()
        return result


class RefreshMutation(graphene.Mutation):
    class Arguments(object):
        refresh_token = graphene.String()

    new_token = graphene.String()

    @mutation_jwt_refresh_token_required
    def mutate(self):
        current_user = get_jwt_identity()
        return RefreshMutation(new_token=create_access_token(identity=current_user))


class AuthMutation(graphene.Mutation):
    class Arguments:
        username = graphene.String()
        password = graphene.String()

    access_token = graphene.String()
    refresh_token = graphene.String()

    def mutate(self, info, username, password):
        refresh_token = create_refresh_token(username)
        access_token = create_access_token(username)
        permission = Permission.query.filter(username=username).first()
        if permission:
            permission.refresh_token = refresh_token
            update_details()
        else:
            permission = Permission(username, password, refresh_token)
            print(permission.refresh_token)
            create_details(permission)
        return AuthMutation(
            access_token, refresh_token
        )


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


class Mutation(graphene.ObjectType):
    auth = AuthMutation.Field()
    refresh_token = RefreshMutation.Field()
    add_community = AddCommunity.Field()
    add_building = AddBuilding.Field()
    add_floor = AddFloor.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
