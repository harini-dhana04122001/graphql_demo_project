import graphene
from flask_graphql_auth import AuthInfoField, create_refresh_token, create_access_token, query_header_jwt_required, \
    mutation_jwt_refresh_token_required, get_jwt_identity
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from sqlalchemy.orm import subqueryload

from building.model import Building
from floor.model import Floor
from permission.model import Permission, PermissionField
from service import create_details, update_details
from community.model import Community
from unit.model import Unit


class UnitObject(SQLAlchemyObjectType):
    class Meta:
        model = Unit
        interfaces = (graphene.relay.Node,)


class FloorObject(SQLAlchemyObjectType):
    class Meta:
        model = Floor
        interfaces = (graphene.relay.Node,)
    unit_field = graphene.List(graphene.String)
    unit = graphene.List(UnitObject)

    # def resolve_floor_name(self, info):
    #     return self.floor_name
    def resolve_unit(self, info):
        # query = Floor.query.options(selectinload(Floor.building))
        # print(query)
        if not self.unit_field:
            units = []
        else:
            units = Unit.query.options(subqueryload(Unit.floor))\
                .with_entities(*[getattr(Unit, field) for field in self.unit_field])\
                .filter_by(floor_id=self.id)
        print(units)
        return [UnitObject(**unit) for unit in units]


class BuildingObject(SQLAlchemyObjectType):
    class Meta:
        model = Building
        interfaces = (graphene.relay.Node,)
    # block_name = graphene.String()
    floor = graphene.List(FloorObject)
    floor_field = graphene.List(graphene.String)
    unit_field = graphene.List(graphene.String)
    # def resolve_block_name(self, info):
    #     return self.block_name

    def resolve_floor(self, info):
        if not self.floor_field:
            floors = []
        else:
            floors = Floor.query.options(subqueryload(Floor.building))\
                .with_entities(Floor.id, *[getattr(Floor, field) for field in self.floor_field])\
                .filter_by(building_id=self.id)
        print(floors)
        return [FloorObject(**floor, unit_field=self.unit_field) for floor in floors]


class CommunityObject(SQLAlchemyObjectType):
    class Meta:
        model = Community
        interfaces = (graphene.relay.Node,)
    # name = graphene.String()
    # agent_name = graphene.String()
    # agent_contact = graphene.String()
    building = graphene.List(BuildingObject)
    building_field = graphene.List(graphene.String)
    floor_field = graphene.List(graphene.String)
    unit_field = graphene.List(graphene.String)
    # def resolve_name(self, info):
    #     return self.name
    #
    # def resolve_agent_name(self, info):
    #     return self.agent_name
    #
    # def resolve_agent_contact(self, info):
    #     return self.agent_contact

    def resolve_building(self, info):
        if not self.building_field:
            buildings = []
        else:
            buildings = Building.query.options(subqueryload(Building.community))\
                .with_entities(Building.id, *[getattr(Building, field) for field in self.building_field])\
                .filter_by(community_id=self.id)
        print(buildings)
        return [BuildingObject(**building, floor_field=self.floor_field, unit_field=self.unit_field) for building in buildings]


class ProtectedCommunity(graphene.Union):
    class Meta:
        types = (CommunityObject, AuthInfoField)


class CommunityObjectTuple(graphene.ObjectType):
    id = graphene.Int
    agent_name = graphene.String()
    name = graphene.String()
    agent_contact = graphene.String()


class Query(graphene.ObjectType):
    node = graphene.relay.Node.Field()
    all_community = SQLAlchemyConnectionField(CommunityObject)
    all_buildings = SQLAlchemyConnectionField(BuildingObject)
    all_floors = SQLAlchemyConnectionField(FloorObject)
    get_community = graphene.List(ProtectedCommunity, token=graphene.String())
    get_community_by_name = graphene.Field(ProtectedCommunity, token=graphene.String(), name=graphene.String())
    community_with_auth = graphene.List(CommunityObject, token=graphene.String())

    def resolve_community_with_auth(self, info, token):
        permission = Permission.query.filter_by(token=token).first()
        permission_field = PermissionField.query.filter_by(permission_id=permission.id, access_type='read').all()
        community_list, building_list, floor_list, unit_list = [], [], [], []
        for i in permission_field:
            if i.model == 'Community':
                community_list.append(f'{i.field}')
            if i.model == 'Building':
                building_list.append(f'{i.field}')
            if i.model == 'Floor':
                floor_list.append(f'{i.field}')
            if i.model == 'Unit':
                unit_list.append(f'{i.field}')
        results = Community.query.options(subqueryload(Community.building))\
            .with_entities(Community.id, *[getattr(Community, field) for field in community_list])
        print(results)
        result_list = []
        result_list.extend([community_list, building_list, floor_list, unit_list])
        print(result_list)
        return [CommunityObject(**result, building_field=building_list, floor_field=floor_list, unit_field=unit_list)
                for result in results]
    '''    results = Community.query\
            .join(Building)\
            .filter_by(community_id=Community.id).join(Floor).filter_by(building_id=Building.id)\
            .with_entities(Community.id, *[getattr(Community, field) for field in community_list],
                           Building.id, *[getattr(Building, field) for field in building_list],
                           *[getattr(Floor, field) for field in floor_list])
        community_data = {}
        building_data = []
        for result in results:
            if result[0] not in community_data:
                # Add the User object to the user_data dictionary
                community_data[result[0]] = CommunityObject(name=result[1], email=result[2])
            # Add the Address object to the address_data list
            building_data.append(BuildingObject(id=result[3], street=result[4], city=result[5], state=result[6]))'''

    @query_header_jwt_required
    def resolve_get_community(self, info):
        print(info.context)
        query = CommunityObject.get_query(info)
        # print(query)
        result = query.all()
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


schema = graphene.Schema(query=Query, mutation=Mutation)
