from django.views.generic.detail import DetailView
from django.views.generic import View, ListView

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