from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator


class PaginationMixin:
    LIMIT_OPTIONS = ["10", "25", "50", "100"]
    DEFAULT_LIMIT = "10"
    DEFAULT_PAGE = "1"
    page_kwarg_mixin = "page"
    limit_kwarg_mixin = "limit"

    def get_pagination_data(self, *args, **kwargs):

        list_queryset = self.get_search_queryset()
        page_number = int(
            self.request.GET.get(self.page_kwarg_mixin) or self.DEFAULT_PAGE
        )
        paginate_by = int(
            self.request.GET.get(self.limit_kwarg_mixin) or self.DEFAULT_LIMIT
        )

        paginator = Paginator(list_queryset, paginate_by)

        try:
            page = paginator.page(page_number)
        except PageNotAnInteger:
            page = paginator.page(self.DEFAULT_PAGE)
        except EmptyPage:
            page = paginator.page(paginator.num_pages)

        page.adjusted_elided_pages = paginator.get_elided_page_range(
            page.number,
            on_each_side=1,
        )

        context = {
            "paginator": paginator,
            "page_obj": page,
            "limit_options": self.LIMIT_OPTIONS,
            "object_list": list_queryset,
        }

        return context
