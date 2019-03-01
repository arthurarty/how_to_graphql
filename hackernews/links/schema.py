import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from .models import Link, Vote
from users.schema import UserType
from django.db.models import Q


class LinkType(DjangoObjectType):
    class Meta:
        model = Link


class VoteType(DjangoObjectType):
    class Meta:
        model = Vote


class Query(graphene.ObjectType):
    link = graphene.Field(LinkType, id=graphene.Int(),
                          url=graphene.String(), description=graphene.String())
    links = graphene.List(LinkType, search=graphene.String(),
                          first=graphene.Int(), skip=graphene.Int())
    votes = graphene.List(VoteType)

    def resolve_links(self, info, search=None, first=None, skip=None, **kwargs):
        qs = Link.objects.all()

        if search:
            filter = (
                Q(url__icontains=search) |
                Q(description__icontains=search)
            )
            return Link.objects.filter(filter)

        if skip:
            qs = qs[skip:]

        if first:
            qs = qs[:first]
        return qs

    def resolve_link(self, info, **kwargs):
        id = kwargs.get('id')

        if id is not None:
            return Link.objects.get(pk=id)

        return None

    def resolve_votes(self, info, **kwargs):
        return Vote.objects.all()


class CreateLink(graphene.Mutation):
    id = graphene.Int()
    url = graphene.String()
    description = graphene.String()
    post_by = graphene.Field(UserType)

    class Arguments:
        url = graphene.String()
        description = graphene.String()

    def mutate(self, info, url, description):
        user = info.context.user or None

        link = Link(url=url, description=description, post_by=user,)
        link.save()

        return CreateLink(
            id=link.id,
            url=link.url,
            description=link.description,
            post_by=link.post_by,
        )


class CreateVote(graphene.Mutation):
    user = graphene.Field(UserType)
    link = graphene.Field(LinkType)

    class Arguments:
        link_id = graphene.Int()

    def mutate(self, info, link_id):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError('You must be logged in to vote!')

        link = Link.objects.filter(id=link_id).first()
        if not link:
            raise Exception('Invalid Link!')

        Vote.objects.create(
            user=user,
            link=link,
        )

        return CreateVote(user=user, link=link)


class Mutation(graphene.ObjectType):
    create_link = CreateLink.Field()
    create_vote = CreateVote.Field()
