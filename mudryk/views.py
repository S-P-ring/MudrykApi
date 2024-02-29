import datetime
import json
from django.http import JsonResponse
from django.views.generic import View

from mudryk.calendar_client import get_lesson_days
from mudryk.models import TeamMember, Faq, Course, Feedback, Lesson, Record, Proposal
from mudryk.telegram_sending import send_record, send_feedback_or_proposal
from mudryk.utils import translate_date


class OurTeamView(View):
    def get(self, request):
        try:
            team_members = TeamMember.objects.all()
        except Exception:
            return JsonResponse(
                {'status': 'error', 'message': 'Team has not any members', 'error_type': '0'})
        serialized_data = []
        for member in team_members:
            member_data = {'name': member.name,
                           'description': member.description,
                           'photo_url': member.photo.url}
            serialized_data.append(member_data)
        return JsonResponse(
            {'status': 'success',
             'message': 'Team information successfully received',
             'team_members': serialized_data}, safe=False, json_dumps_params={'ensure_ascii': False})


class FaqView(View):
    def get(self, request):
        try:
            faqs = Faq.objects.all()
        except Exception:
            return JsonResponse(
                {'status': 'error', 'message': 'Faq is empty.', 'error_type': '0'})
        serialized_data = []
        for question in faqs:
            answer = {'question': question.question,
                      'answer': question.answer}
            serialized_data.append(answer)
        return JsonResponse(
            {'status': 'success',
             'message': 'Faq information successfully received',
             'faq': serialized_data}, safe=False, json_dumps_params={'ensure_ascii': False})


class OurCoursesView(View):
    def get(self, request):
        try:
            courses_list = Course.objects.all()
        except Exception:
            return JsonResponse(
                {'status': 'error', 'message': 'Courses list is empty is empty.', 'error_type': '0'})
        serialized_data = []
        for course in courses_list:
            main_description = []
            for text in course.text_for_course.all():
                main_description.append(text.text)
            text_list = {}
            for text_with_list in course.text_with_list_for_course.all():
                list_item = []
                for li_item in text_with_list.list_item_for_text.all():
                    list_item.append(li_item.text)
                text_list[f'{text_with_list.title}'] = list_item

            course_info = {'title': course.name,
                           'max_members': course.max_members,
                           'price': course.price,
                           'main_description': main_description,
                           'li_text': text_list}
            serialized_data.append(course_info)
        return JsonResponse(
            {'status': 'success',
             'message': 'Courses list successfully received',
             'courses': serialized_data}, safe=False, json_dumps_params={'ensure_ascii': False})


class FeedbackView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            pib = data['name'] + ' ' + data['surname']
            if data['selectedOption'] == 'feedback':
                Feedback.objects.create(name=data['name'], surname=data['surname'], lesson=data['lesson'],
                                        email=data['email'], feedback_text=data['message'],
                                        phone_number=data['phone'])
                send_feedback_or_proposal(data['selectedOption'], pib, email=data['email'],
                                          text=data['message'], phone_number=data['phone'], lesson=data['lesson'])
            elif data['selectedOption'] == 'proposal':
                Proposal.objects.create(name=data['name'], surname=data['surname'], lesson=data['lesson'],
                                        email=data['email'], proposal_text=data['message'],
                                        phone_number=data['phone'])
                send_feedback_or_proposal(data['selectedOption'], pib, email=data['email'],
                                          text=data['message'], phone_number=data['phone'], lesson=data['lesson'])
            else:
                return JsonResponse({'status': 'error', 'message': 'Now can not send message', 'error_type': '0'})

            return JsonResponse({'status': 'success', 'message': 'Message was sent'})
        except Exception:
            return JsonResponse({'status': 'error', 'message': 'Now can not send message', 'error_type': '0'})


def get_schedule(request):
    if request.method == 'GET':
        courses_list = Course.objects.all().values('name')
        schedule = {}
        for selected_course in courses_list:
            selected_course = selected_course['name']
            try:
                lesson_days = list(get_lesson_days(selected_course))
                datetime_list = []
                for lesson_day in lesson_days:
                    for time in lesson_day['times']:
                        date_and_time = lesson_day['date'] + ' ' + time + '+02:00'
                        datetime_list.append(date_and_time)
                lessons = Lesson.objects.all()
                dates_to_delete = []
                for lesson in lessons:
                    if lesson.current_participants == lesson.max_participants:
                        dates_to_delete.append(lesson.datetime_start)
                for date_to_delete in dates_to_delete:
                    for lesson_day in lesson_days:
                        for time in lesson_day['times']:
                            date_and_time = lesson_day['date'] + ' ' + time + '+02:00'
                            if datetime.datetime.strftime(date_to_delete, '%Y-%m-%d %H:%M:%S') == \
                                    date_and_time.split('+')[0]:
                                lesson_day['times'].remove(time)
                                if len(lesson_day['times']) == 0:
                                    lesson_days.remove(lesson_day)
                for day in lesson_days:
                    day['day_str'] = translate_date(day['day_str'])

                schedule[f'{selected_course}'] = lesson_days
            except Exception:
                return JsonResponse(
                    {'status': 'error', 'message': 'Something went wrong in schedule calendar.', 'error_type': '0'})

        contains_empty = any(not sublist for sublist in schedule)
        if contains_empty:
            return JsonResponse({'status': 'error', 'message': 'It seems that schedule is empty.', 'error_type': '1'})

        return JsonResponse({'status': 'success', 'schedule': schedule})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method', 'error_type': '2'})


def submit_record(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        selected_course = data.get('selectedCourse', '')
        selected_day = data.get('selectedDate', '')
        selected_time = data.get('selectedTime', '')
        if selected_time != '':
            selected_time += '+02:00'
        parent_name = data.get('parentName', '')
        parent_surname = data.get('parentSurname', '')
        parent_name = parent_name + ' ' + parent_surname
        child_name = data.get('childName', '')
        child_surname = data.get('childSurname', '')
        child_name = child_name + ' ' + child_surname
        email = data.get('email', '')
        phone = data.get('phone', '')
        date_and_time = selected_day + ' ' + selected_time
        try:
            if Lesson.objects.filter(title=selected_course, datetime_start=date_and_time).exists():
                lesson = Lesson.objects.get(title=selected_course, datetime_start=date_and_time)
                current_participants = lesson.current_participants + 1
                lesson.current_participants = current_participants
                lesson.save()
                Record.objects.create(parent_name=parent_name, child_name=child_name, email=email, phone_number=phone,
                                      lesson=lesson)
                send_record(selected_course, selected_day, selected_time, parent_name, child_name, email, phone)
            else:
                max_members = Course.objects.get(name=selected_course).max_members
                lesson = Lesson.objects.create(title=selected_course, datetime_start=date_and_time,
                                               max_participants=max_members, current_participants=1)
                Record.objects.create(parent_name=parent_name, child_name=child_name, email=email, phone_number=phone,
                                      lesson=lesson)
                send_record(selected_course, selected_day, selected_time, parent_name, child_name, email, phone)
        except Exception:
            return JsonResponse(
                {'status': 'error', 'message': 'Something went wrong in record process.', 'error_type': '0'},
                safe=False, json_dumps_params={'ensure_ascii': False})

        return JsonResponse({'status': 'success', 'message': 'Record was sent successfully.'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method', 'error_type': '1'})
