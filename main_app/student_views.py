import json
import math
from datetime import datetime
from .models import Questionnaire,Response
import uuid
import os

from django.db import transaction
from django.db.models import F
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import (HttpResponseRedirect, get_object_or_404,
                              redirect, render)
from django.urls import reverse
from django.shortcuts import render, get_list_or_404
from django.views.decorators.csrf import csrf_exempt

from .forms import *
from .models import *


def merchant_home(request):
    student = get_object_or_404(Merchant, admin=request.user)
    # total_subject = Subject.objects.filter(course=student.course).count()
    total_attendance = AttendanceReport.objects.filter(student=student).count()
    total_present = AttendanceReport.objects.filter(student=student, status=True).count()
    if total_attendance == 0:  # Don't divide. DivisionByZero
        percent_absent = percent_present = 0
    else:
        percent_present = math.floor((total_present/total_attendance) * 100)
        percent_absent = math.ceil(100 - percent_present)
    subject_name = []
    data_present = []
    data_absent = []
    # subjects = Subject.objects.filter(course=student.course)
    # for subject in subjects:
    #     attendance = Attendance.objects.filter(subject=subject)
    #     present_count = AttendanceReport.objects.filter(
    #         attendance__in=attendance, status=True, student=student).count()
    #     absent_count = AttendanceReport.objects.filter(
    #         attendance__in=attendance, status=False, student=student).count()
    #     subject_name.append(subject.name)
    #     data_present.append(present_count)
    #     data_absent.append(absent_count)
    context = {
        'total_attendance': total_attendance,
        'percent_present': percent_present,
        'percent_absent': percent_absent,
        # 'total_subject': total_subject,
        # 'subjects': subjects,
        'data_present': data_present,
        'data_absent': data_absent,
        'data_name': subject_name,
        'page_title': 'Merchant Homepage'

    }
    return render(request, 'student_template/home_content.html', context)


@ csrf_exempt
def merchant_view_attendance(request):
    student = get_object_or_404(Merchant, admin=request.user)
    if request.method != 'POST':
        # course = get_object_or_404(Course, id=student.course.id)
        context = {
            # 'subjects': Subject.objects.filter(course=course),
            'page_title': 'View Attendance'
        }
        return render(request, 'student_template/merchant_view_attendance.html', context)
    else:
        subject_id = request.POST.get('subject')
        start = request.POST.get('start_date')
        end = request.POST.get('end_date')
        try:
            subject = get_object_or_404(Questionnaire, id=subject_id)
            start_date = datetime.strptime(start, "%Y-%m-%d")
            end_date = datetime.strptime(end, "%Y-%m-%d")
            attendance = Attendance.objects.filter(
                date__range=(start_date, end_date), subject=subject)
            attendance_reports = AttendanceReport.objects.filter(
                attendance__in=attendance, student=student)
            json_data = []
            for report in attendance_reports:
                data = {
                    "date":  str(report.attendance.date),
                    "status": report.status
                }
                json_data.append(data)
            return JsonResponse(json.dumps(json_data), safe=False)
        except Exception as e:
            return None


def merchant_apply_leave(request):
    form = LeaveReportStudentForm(request.POST or None)
    student = get_object_or_404(Merchant, admin_id=request.user.id)
    context = {
        'form': form,
        'leave_history': LeaveReportStudent.objects.filter(student=student),
        'page_title': 'Apply for leave'
    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.student = student
                obj.save()
                messages.success(
                    request, "Application for leave has been submitted for review")
                return redirect(reverse('merchant_apply_leave'))
            except Exception:
                messages.error(request, "Could not submit")
        else:
            messages.error(request, "Form has errors!")
    return render(request, "student_template/merchant_apply_leave.html", context)


def merchant_feedback(request):
    form = FeedbackStudentForm(request.POST or None)
    student = get_object_or_404(Merchant, admin_id=request.user.id)
    context = {
        'form': form,
        'feedbacks': FeedbackStudent.objects.filter(student=student),
        'page_title': 'Merchant Feedback'

    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.student = student
                obj.save()
                messages.success(
                    request, "Feedback submitted for review")
                return redirect(reverse('merchant_feedback'))
            except Exception:
                messages.error(request, "Could not Submit!")
        else:
            messages.error(request, "Form has errors!")
    return render(request, "student_template/merchant_feedback.html", context)


def merchant_view_profile(request):
    student = get_object_or_404(Merchant, admin=request.user)
    form = MerchantEditForm(request.POST or None, request.FILES or None,
                           instance=student)
    context = {'form': form,
               'page_title': 'View/Edit Profile'
               }
    if request.method == 'POST':
        try:
            if form.is_valid():
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                password = form.cleaned_data.get('password') or None
                address = form.cleaned_data.get('address')
                gender = form.cleaned_data.get('gender')
                passport = request.FILES.get('profile_pic') or None
                admin = student.admin
                if password != None:
                    admin.set_password(password)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    admin.profile_pic = passport_url
                admin.first_name = first_name
                admin.last_name = last_name
                admin.address = address
                admin.gender = gender
                admin.save()
                student.save()
                messages.success(request, "Profile Updated!")
                return redirect(reverse('merchant_view_profile'))
            else:
                messages.error(request, "Invalid Data Provided")
        except Exception as e:
            messages.error(request, "Error Occured While Updating Profile " + str(e))

    return render(request, "student_template/merchant_view_profile.html", context)


@csrf_exempt
def student_fcmtoken(request):
    token = request.POST.get('token')
    student_user = get_object_or_404(CustomUser, id=request.user.id)
    try:
        student_user.fcm_token = token
        student_user.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


def merchant_view_notification(request):
    student = get_object_or_404(Merchant, admin=request.user)
    notifications = NotificationMerchant.objects.filter(student=student)
    context = {
        'notifications': notifications,
        'page_title': "View Notifications"
    }
    return render(request, "student_template/merchant_view_notification.html", context)

def merchant_view_compliance(request):
    compliances = Compliance.objects.all()  # Retrieve all compliance records
    context = {
        'compliances': compliances,
        'page_title': "View Compliance"
    }
    return render(request, "student_template/merchant_view_compliance.html", context)

def has_response(questionnaire):
    """
    Check if a response exists for the given questionnaire.
    """
    try:
        response = Response.objects.get(questionnaire=questionnaire)
        return True
    except Response.DoesNotExist:
        return False
    

def merchant_view_response(request, q_id):
    questionnaires = get_list_or_404(Questionnaire, q_id=q_id)
    responses = Response.objects.filter(q_id=q_id)

    if not responses.exists():
        context = {
            'page_title': "View Responses",
            'no_responses': True,
            'show_edit_column': False,  # Set to False if there are no responses
        }
        return render(request, "student_template/merchant_view_response.html", context)

    questionnaire_dict = {}
    for q in questionnaires:
        myuuid = uuid.uuid4()      
        questionnaire_dict[myuuid] = {'question': q.question}
    questions = list(questionnaire_dict.values())

    edit_counter_value = responses.first().edit_counter

    # if request.method == 'POST':
    #     # Handle the form submission
    #     for q, response in zip(questions, responses):
    #         response_text = request.POST.get(f"edit-response-1-{response.id}")
    #         response.Edit1_response = response_text
    #         response.save()

    #     return HttpResponseRedirect(reverse('merchant_view_response', args=[q_id]))

    rows = [] 
    for q, response in zip(questions, responses):
        rows.append({'question': q['question'], 'response': response.response ,'question_id':response.question_id,'id':response.id,'edit1_response':response.Edit1_response,'edit2_response':response.Edit2_response,'edit3_response':response.Edit3_response})

    context = {
        'rows': rows,
        'page_title': "View Responses",
        'no_responses': False,
        'edit_counter_value': 3- edit_counter_value,
        'show_edit_column': True,  # Set to True since there are responses
    }
    return render(request, "student_template/merchant_view_response.html", context)    

def submit_responses(request):
    if request.method == 'POST':
        # Get the merchant ID from the request or session, replace with your logic
        merchant_id = request.user.merchant.id if request.user.merchant else None
        print('check')
        if merchant_id is not None:
            # Assuming q_id is the same for all questions on the page
            q_id = request.POST.get('q_id')
            questionnaire_id = request.POST.get('questionnaire_id')

            # Check if responses already exist for the given questionnaire and merchant
            existing_responses = Response.objects.filter(
                merchant_id=merchant_id,
                q_id=q_id,
                questionnaire_id=questionnaire_id
            )

            if existing_responses.exists():
                # If responses exist, show a message indicating that data is already present
                return render(request, 'student_template/data_already_present.html', {'questionnaire_id': questionnaire_id})

            # Use transaction.atomic() to ensure that either all changes are committed, or none
            with transaction.atomic():
                # Iterate through POST data to extract and insert responses
                for key, value in request.POST.items():
                    if key.startswith('response_'):
                        print('check2')
                        # Extract question ID from the key
                        question_id = key.replace('response_', '')

                        # Create a new Response entry
                        response = Response.objects.create(
                            merchant_id=merchant_id,
                            q_id=q_id,
                            questionnaire_id=questionnaire_id,
                            question_id=question_id,
                            response=value
                        )

                       # Handle file uploads
                        file_key = f'file_{question_id}'
                        if file_key in request.FILES:
                            print('a')
                            file = request.FILES[file_key]

                            # Generate a unique filename to avoid overwriting existing files
                            # filename = os.path.join('uploads', str(response.id) + '_' + file.name)
                            filename=file.name
                            # Save the file to the designated folder
                            with open(filename, 'wb') as destination:
                                for chunk in file.chunks():
                                    destination.write(chunk)

                            # Save the filename in the database
                            response.file = filename
                            print('b')
                            response.save()

            return redirect('merchant_assigned_compliance')  # Redirect to the 'merchant_assigned_compliance' page

    # If the request is not a POST request, render the form
    return render(request, 'merchant_assigned_compliance.html', {'questionnaires': Questionnaire.objects.all()})

def edited_responses(request):
    if request.method == 'POST':
        # Get the merchant ID from the request or session, replace with your logic
        merchant_id = request.user.merchant.id if request.user.merchant else None

        if merchant_id is not None:
            # Lists to store response IDs and values
            response_ids = []
            response_values = []

            for key, value in request.POST.items():
                if key.startswith('edit-response'):
                    # Extract response ID from the key
                    response_id = key.replace('edit-response', '')
                    # Append response ID and value to the lists
                    response_ids.append(response_id)
                    response_values.append(value)
                    print('a')

            # Update the corresponding Response entries
            for i in range(len(response_ids)):
                try:
                    response = Response.objects.get(
                        id=response_ids[i],
                        merchant_id=merchant_id
                    )
                    print(response.edit_counter)
                    print('b')
                                                            # Use the edit_counter dynamically to update Edit_response columns
                    for j in range(response.edit_counter+1,response.edit_counter +2):
                        edit_column_name = f"Edit{j}_response"
                        response_text = response_values[i]
                        setattr(response, edit_column_name, response_text)

                         # Handling file uploads
                        file_field_name = f"Edit{j}_file"
                        
                        print(file_field_name)

                        file_upload = f'file_{response_id}'
 
                        print(file_upload)
                        
                        if file_upload in request.FILES:
                           file=request.FILES[file_upload]                           
                           print('ABCD')   
                        # file_upload = request.FILES.get(file_field_name)
                        # if file_upload:
                            # Generate a unique filename to avoid overwriting existing files
                           filename = file.name
                           print(filename)
                            
                           file_path = default_storage.save(filename, ContentFile(file.read()))

                           setattr(response, file_field_name, file_path)
                                                        
                        print('d')
                        print(edit_column_name)
                        print('e')
                        print(response_text)
                        response.save()

                    print(f"Updated response with ID {response_ids[i]}")
                    response.edit_counter = F('edit_counter') + 1
                    response.save(update_fields=['edit_counter'])
                except Exception as e:
                    print(f"An error occurred: {e}")

    return render(request, 'student_template/merchant_view_response.html', {'questionnaires': Questionnaire.objects.all()})


def merchant_create_form(request, q_id):
    questionnaires = get_list_or_404(Questionnaire, q_id=q_id)
    
    # Create a list to store all questions from different rows
    all_questions = []
    
    for questionnaire in questionnaires:
        # Split the questions from each row and add them to the list
        questions = questionnaire.question.splitlines()
        all_questions.extend(questions)

    context = {
        'questionnaires': questionnaires,
        'all_questions': all_questions,
        'page_title': f"Respond to Questionnaire(s)",
    }

    return render(request, "student_template/respond_to_questionnaire.html", context)

def merchant_assigned_compliance(request):
    current_merchant = request.user.merchant  
    assigned_questionnaires = Questionnaire.objects.filter(merchant=current_merchant)
    
    # Create a list of dictionaries containing both q_id and questionnaire name
    questionnaire_data = [{'q_id': questionnaire.q_id, 'name': questionnaire.name} for questionnaire in assigned_questionnaires]

    context = {
        'assigned_questionnaires': assigned_questionnaires,
        'page_title': "View Compliance Questionnaires for Merchant",
    }
    return render(request, "student_template/merchant_assigned_compliance.html", context)


def merchant_edit_response(request, q_id):
    questionnaires = get_list_or_404(Questionnaire, q_id=q_id)
    responses = Response.objects.filter(q_id=q_id)

    # Check if there are responses for the given questionnaire
    if not responses.exists():
        # If no responses are found, render a template with a message
        context = {
            'page_title': "Edit Responses",
            'no_responses': True,
        }
        return render(request, "student_template/merchant_edit_response.html", context)

    # Create a dictionary to map q_id to the respective question
    questionnaire_dict = {}
    for q in questionnaires:
        myuuid = uuid.uuid4()      
        questionnaire_dict[myuuid] = {'question': q.question}
    questions = list(questionnaire_dict.values())

    # Fetch the edit_counter value for the specified q_id
    edit_counter_value = responses.first().edit_counter

    # Create a list of dictionaries for rows
    rows = [] 
    for q, response in zip(questions, responses):
        rows.append({'question': q['question'], 'response': response.response})    

    context = {
        'rows': rows,
        'page_title': "Edit Responses",
        'no_responses': False,  # Set to False since there are responses
        'edit_counter_value': 3 - edit_counter_value,
    }
    return render(request, "student_template/merchant_edit_response.html", context)


def student_view_result(request):
    student = get_object_or_404(Merchant, admin=request.user)
    results = StudentResult.objects.filter(student=student)
    context = {
        'results': results,
        'page_title': "View Results"
    }
    return render(request, "student_template/student_view_result.html", context)


#library

def view_books(request):
    books = Book.objects.all()
    context = {
        'books': books,
        'page_title': "Library"
    }
    return render(request, "student_template/view_books.html", context)

