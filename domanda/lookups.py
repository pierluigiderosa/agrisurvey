from ajax_select import register, LookupChannel
from .models import catastale_new
from django.db.models import Value as V
from django.db.models.functions import Concat,Substr


@register('catastali')
class ThingsLookup(LookupChannel):

    model = catastale_new

    def check_auth(self, request):
        if request.user.is_authenticated:
            return True

    def get_query(self, q, request):
        queryset = self.model.objects.annotate(search_name=Concat('comune', V(' '),Substr('foglio',5,3),V(' '),'part'))
        return queryset.filter(search_name__icontains=q)[:5]

    # def format_item_display(self, item):
    #     return u"<span class='tag'>%s</span>" % item.foglio