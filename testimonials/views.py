from django.views.generic.detail import DetailView
from django.views.generic import View, ListView
from django.views.generic.edit import CreateView
from django.contrib import messages

from mezzanine.conf import settings
from mezzanine.utils.views import paginate

from testimonials.models import Testimonial


class TestimonialView(DetailView):
    template_name = "testimonials/testimonial.html"
    model = Testimonial


class RandomTestimonialView(View):
    testimonial_view = staticmethod(TestimonialView.as_view())

    def dispatch(self, request, *args, **kwargs):
        testimonial = Testimonial.objects.order_by('?')[0]
        kwargs['slug'] = testimonial.slug
        return self.testimonial_view(request, *args, **kwargs)


class TestimonialListView(ListView):
    template_name = "testimonials/testimonial_list.html"
    context_object_name = 'testimonials'
    model = Testimonial

    def get_queryset(self):
        return super().get_queryset().order_by('?')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['testimonials'] = paginate(context['testimonials'],
                                           self.request.GET.get("page", 1),
                                           5,
                                           settings.MAX_PAGING_LINKS)
        return context


class TestimonialCreateView(CreateView):
    model = Testimonial
    fields = ('title', 'author', 'content')

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, "Your testimonial has been saved.")
        return super().form_valid(form)

