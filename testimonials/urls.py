from django.conf.urls import patterns, url

from testimonials.views import (TestimonialView,
                                RandomTestimonialView,
                                TestimonialListView,
                                TestimonialCreateView)

urlpatterns = patterns(
    '',
    url(r'^/list/$', TestimonialListView.as_view(), name='list_testimonial'),
    url(r'^/create/$', TestimonialCreateView.as_view(), name='create_testimonial'),
    url(r'^/testimonial/$', RandomTestimonialView.as_view(), name='random_testimonial'),
    url(r'^/i/(?P<slug>[-_\w]+)/$', TestimonialView.as_view(), name='testimonial'))