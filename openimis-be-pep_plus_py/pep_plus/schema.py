"""
PEP+ GraphQL Schema
Aggregates all queries and mutations for the PEP+ module
"""
import graphene
from .gql_queries import Query
from .gql_mutations import Mutation


# Export the Query and Mutation classes for openIMIS to discover
__all__ = ['Query', 'Mutation']
