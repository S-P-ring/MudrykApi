from django.urls import path
from mudryk.views import OurTeamView, FaqView, OurCoursesView, FeedbackView, submit_record, get_schedule

urlpatterns = [
    path('get_team/', OurTeamView.as_view(), name='get_team'),
    path('get_faq/', FaqView.as_view(), name='get_faq'),
    path('get_courses/', OurCoursesView.as_view(), name='get_courses'),
    path('post_feedback/', FeedbackView.as_view(), name='post_feedback'),
    path('get_schedule/', get_schedule, name='get_schedule'),
    path('submit_record/', submit_record, name='submit_record'),
]