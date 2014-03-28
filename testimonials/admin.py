from copy import deepcopy

from django.contrib import admin

from mezzanine.core.admin import DisplayableAdmin

from testimonials.models import Testimonial

testimonial_fieldsets = deepcopy(DisplayableAdmin.fieldsets)
testimonial_fieldsets[0][1]["fields"] += ("author", "content")


class TestimonialAdmin(DisplayableAdmin):
    fieldsets = testimonial_fieldsets
    list_display = ("title", "author", "status", "short_content", "admin_link")

    def short_content(self, testimonial):
        return testimonial.content


admin.site.register(Testimonial, TestimonialAdmin)
