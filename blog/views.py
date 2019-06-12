""" Blog views module. """
import os
from django.conf import settings
from django.http import Http404
from django.utils.decorators import method_decorator
from django.views.generic import DetailView
import markdown
from common.decorators import cache_public
from blog.models import Entry


@method_decorator(cache_public(60 * 15), name='dispatch')
class EntryView(DetailView):
    """ Blog entry view. """

    model = Entry
    template_name = 'blog/entry.html'

    def get_object(self):
        """ Raise 404 for unpublished entries. """
        obj = super().get_object()
        if not self.request.user.is_authenticated and not obj.published:
            raise Http404()
        return obj

    def get_context_data(self, **kwargs):
        """ Insert data into template context. """
        context = super().get_context_data(**kwargs)
        obj = context['object']
        context['page_title'] = obj.title
        entries_base = os.path.join(settings.BASE_DIR, 'blog', 'entries')

        # Entry markdown file to paragraphs.
        entry_file = os.path.join(entries_base, '%s.md' % obj.slug)
        with open(entry_file) as entry_fd:
            context['entry'] = markdown.markdown(entry_fd.read())

        # Refs file to list of links, one per line.
        context['refs'] = []
        refs_file = os.path.join(entries_base, '%s.refs' % obj.slug)
        if os.path.isfile(refs_file):
            with open(refs_file) as refs_fd:
                for ref in refs_fd.readlines():
                    context['refs'].append(ref.strip())

        # Static image links.
        context['static_img'] = 'blog/img/%s.jpg' % obj.slug

        return context
