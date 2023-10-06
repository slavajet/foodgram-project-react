from rest_framework.pagination import PageNumberPagination

PAGE_SIZE = 6


class Paginator(PageNumberPagination):
    """
    Пользовательский класс паджинации.
    Attributes:
        page_size: Количество элементов на странице.
        page_size_query_param: Параметр запроса для указания количества элементов на странице.
        recipes_limit_query_param: Параметр запроса для ограничения количества рецептов.
    """
    page_size = PAGE_SIZE
    page_size_query_param = 'limit'
    recipes_limit_query_param = 'recipes_limit'
