from rest_framework.pagination import PageNumberPagination


class CustomPagesPaginator(PageNumberPagination):
    page_size_query_param = 'limit'
