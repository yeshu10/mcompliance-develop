
import json
import requests
from django.forms.formsets import formset_factory
from django.db.models import Count
from django.forms import modelformset_factory
import csv
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import (HttpResponse, HttpResponseRedirect,
                              get_object_or_404, redirect, render)
from django.templatetags.static import static
from django.core.files.storage import default_storage
from io import TextIOWrapper
from django.core.files.base import ContentFile
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import UpdateView

from .forms import *
from .models import *


def admin_home(request):
    total_staff = Provider.objects.all().count()
    total_students = Merchant.objects.all().count()
    subjects = Questionnaire.objects.all()
    total_subject = subjects.count()
    total_course = Compliance.objects.all().count()
    attendance_list = Attendance.objects.filter(subject__in=subjects)
    total_attendance = attendance_list.count()
    attendance_list = []
    subject_list = []
    for subject in subjects:
        attendance_count = Attendance.objects.filter(subject=subject).count()
        subject_list.append(subject.name[:7])
        attendance_list.append(attendance_count)

    # Total Subjects and students in Each Course
    course_all = Compliance.objects.all()
    course_name_list = []
    subject_count_list = []
    student_count_list_in_course = []

    # for compliance in course_all:
    #     # subjects = Subject.objects.filter(compliance_id=course.id).count()
    #     # students = Merchant.objects.filter(compliance_id=course.id).count()
    #     course_name_list.append(course.name)
    #     subject_count_list.append(subjects)
    #     student_count_list_in_course.append(students)
    
    # subject_all = Subject.objects.all()
    # subject_list = []
    # student_count_list_in_subject = []
    # for subject in subject_all:
    #     course = Compliance.objects.get(id=subject.course.id)
    #     student_count = Merchant.objects.filter(course_id=course.id).count()
    #     subject_list.append(subject.name)
    #     student_count_list_in_subject.append(student_count)


    # For Students
    student_attendance_present_list=[]
    student_attendance_leave_list=[]
    student_name_list=[]

    students = Merchant.objects.all()
    for student in students:
        
        attendance = AttendanceReport.objects.filter(student_id=student.id, status=True).count()
        absent = AttendanceReport.objects.filter(student_id=student.id, status=False).count()
        leave = LeaveReportStudent.objects.filter(student_id=student.id, status=1).count()
        student_attendance_present_list.append(attendance)
        student_attendance_leave_list.append(leave+absent)
        student_name_list.append(student.admin.first_name)

    context = {
        'page_title': "Administrative Dashboard",
        'total_students': total_students,
        'total_staff': total_staff,
        'total_course': total_course,
        'total_subject': total_subject,
        'subject_list': subject_list,
        'attendance_list': attendance_list,
        'student_attendance_present_list': student_attendance_present_list,
        'student_attendance_leave_list': student_attendance_leave_list,
        "student_name_list": student_name_list,
        # "student_count_list_in_subject": student_count_list_in_subject,
        "student_count_list_in_course": student_count_list_in_course,
        "course_name_list": course_name_list,

    }
    return render(request, 'hod_template/home_content.html', context)


def add_provider(request):
    form = ProviderForm(request.POST or None, request.FILES or None)
    context = {'form': form, 'page_title': 'Add Provider'}
    if request.method == 'POST':
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            address = form.cleaned_data.get('address')
            email = form.cleaned_data.get('email')
            gender = form.cleaned_data.get('gender')
            password = form.cleaned_data.get('password')
            course = form.cleaned_data.get('course')
            passport = request.FILES.get('profile_pic')
            fs = FileSystemStorage()
            filename = fs.save(passport.name, passport)
            passport_url = fs.url(filename)
            try:
                user = CustomUser.objects.create_user(
                    email=email, password=password, user_type=2, first_name=first_name, last_name=last_name, profile_pic=passport_url)
                user.gender = gender
                user.address = address
                user.provider.course = course
                user.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_provider'))

            except Exception as e:
                messages.error(request, "Could Not Add " + str(e))
        else:
            messages.error(request, "Please fulfil all requirements")

    return render(request, 'hod_template/add_provider_template.html', context)


def add_merchant(request):
    student_form = MerchantForm(request.POST or None, request.FILES or None)
    context = {'form': student_form, 'page_title': 'Add Merchant'}
    if request.method == 'POST':
        if student_form.is_valid():
            first_name = student_form.cleaned_data.get('first_name')
            last_name = student_form.cleaned_data.get('last_name')
            address = student_form.cleaned_data.get('address')
            email = student_form.cleaned_data.get('email')
            gender = student_form.cleaned_data.get('gender')
            password = student_form.cleaned_data.get('password')
            course = student_form.cleaned_data.get('course')
            session = student_form.cleaned_data.get('session')
            passport = request.FILES['profile_pic']
            fs = FileSystemStorage()
            filename = fs.save(passport.name, passport)
            passport_url = fs.url(filename)
            try:
                user = CustomUser.objects.create_user(
                    email=email, password=password, user_type=3, first_name=first_name, last_name=last_name, profile_pic=passport_url)
                user.gender = gender
                user.address = address
                user.merchant.session = session
                user.merchant.course = course
                user.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_merchant'))
            except Exception as e:
                messages.error(request, "Could Not Add: " + str(e))
        else:
            messages.error(request, "Could Not Add: ")
    return render(request, 'hod_template/add_merchant_template.html', context)


def add_compliance(request):
    form = ComplianceForm(request.POST or None)
    context = {
        'form': form,
        'page_title': 'Add Compliance'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            try:
                compliance = Compliance()
                compliance.name = name
                compliance.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_compliance'))
            except:
                messages.error(request, "Could Not Add")
        else:
            messages.error(request, "Could Not Add")
    return render(request, 'hod_template/add_compliance_template.html', context)

# def add_questionnaire(request):
#     if request.method == 'POST':
#         form = QuestionnaireForm(request.POST)
#         if form.is_valid():
#             name = form.cleaned_data.get('name')
#             compliance = form.cleaned_data.get('compliance')
#             provider = form.cleaned_data.get('provider')
#             questions = form.cleaned_data.get('question').split(',')

#             try:
#                 for question_text in questions:
#                     new_questionnaire = Questionnaire(
#                         name=name,
#                         provider=provider,
#                         compliance=compliance,
#                         question=question_text
#                     )
#                     new_questionnaire.q_id = new_questionnaire.generate_id()  # Set 'q_id' value
#                     new_questionnaire.save()
                
#                 messages.success(request, "Successfully Added")
#                 return redirect(reverse('add_questionnaire'))
#             except Exception as e:
#                 messages.error(request, f"Error adding the questionnaire: {str(e)}")
#         else:
#             messages.error(request, "Form is not valid. Please check your inputs.")
#     else:
#         form = QuestionnaireForm()

#     context = {
#         'form': form,
#         'page_title': 'Add Questionnaires'
#     }
#     return render(request, 'hod_template/add_questionnaire_template.html', context)

# working fine but without id
def add_questionnaire(request):
    if request.method == 'POST':
        form = QuestionnaireForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            compliance = form.cleaned_data.get('compliance')
            provider = form.cleaned_data.get('provider')
            # Extract questions from the request.POST dictionary
            questions = [v for k, v in request.POST.items() if k.startswith('question')]

            ques_id = Questionnaire.generate_id()

            try:
                i=0
                for question_text in questions:
                    i=i+1
                    new_questionnaire = Questionnaire(
                        name=name,
                        provider=provider,
                        compliance=compliance,
                        question=question_text,
                        question_id=f"{ques_id}.{i}"
                    )
                    new_questionnaire.q_id=ques_id
                    new_questionnaire.save()
                    # new_questionnaire.q_id = new_questionnaire.generate_id()  # Set 'q_id' value
                    # new_questionnaire.save()
                                    
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_questionnaire'))
            except Exception as e:
                messages.error(request, f"Error adding the questionnaire: {str(e)}")
        else:
            messages.error(request, "Form is not valid. Please check your inputs.")
    else:
        form = QuestionnaireForm()

    context = {
        'form': form,
        'page_title': 'Add Questionnaires'
    }
    return render(request, 'hod_template/add_questionnaire_template.html', context)


# def add_questionnaire(request):
#     # Create a formset for the QuestionnaireForm
#     QuestionnaireFormSet = modelformset_factory(Questionnaire, form=QuestionnaireForm, extra=0)

#     if request.method == 'POST':
#         formset = QuestionnaireFormSet(request.POST)
#         if formset.is_valid():
#             # Iterate through the formset to save each question separately
#             for form in formset:
#                 name = form.cleaned_data.get('name')
#                 compliance = form.cleaned_data.get('compliance')
#                 provider = form.cleaned_data.get('provider')
#                 question = form.cleaned_data.get('question')

#                 try:
#                     new_questionnaire = Questionnaire(
#                         name=name,
#                         provider=provider,
#                         compliance=compliance,
#                         question=question
#                     )
#                     new_questionnaire.save()
#                 except Exception as e:
#                     messages.error(request, f"Error adding the questionnaire: {str(e)}")
#             messages.success(request, "Successfully Added")
#             return redirect(reverse('add_questionnaire'))
#         else:
#             messages.error(request, "Form is not valid. Please check your inputs.")
#     else:
#         formset = QuestionnaireFormSet(queryset=Questionnaire.objects.none())

#     context = {
#         'formset': formset,
#         'page_title': 'Add Questionnaires'
#     }
#     return render(request, 'hod_template/add_questionnaire_template.html', context)

# without csv single question 
# def add_questionnaire(request):
#     if request.method == 'POST':
#         form = QuestionnaireForm(request.POST)
#         if form.is_valid():
#             name = form.cleaned_data.get('name')
#             compliance = form.cleaned_data.get('compliance')
#             provider = form.cleaned_data.get('provider')
#             question = form.cleaned_data.get('question')

#             try:
#                 new_questionnaire = Questionnaire(
#                     name=name,
#                     provider=provider,
#                     compliance=compliance,
#                     question=question  # Set the question field
#                 )
#                 new_questionnaire.save()
#                 messages.success(request, "Successfully Added")
#                 return redirect(reverse('add_questionnaire'))
#             except Exception as e:
#                 messages.error(request, f"Error adding the questionnaire: {str(e)}")
#         else:
#             messages.error(request, "Form is not valid. Please check your inputs.")
#     else:
#         form = QuestionnaireForm()

#     context = {
#         'form': form,
#         'page_title': 'Add Questionnaires'
#     }
#     return render(request, 'hod_template/add_questionnaire_template.html', context)


#for multiple
# def assign_questionnaire(request):
#     if request.method == 'POST':
#         form = QuestionnaireassignForm(request.POST)
#         if form.is_valid():
#             selected_merchants = form.cleaned_data.get('merchant', [])
#             selected_questionnaires = form.cleaned_data.get('name', [])

#             try:
#                 for questionnaire in selected_questionnaires:
#                     questionnaire.merchant.add(*selected_merchants)

#                 messages.success(request, "Successfully Added")
#                 return redirect('assign_questionnaire')
#             except Exception as e:
#                 messages.error(request, f"Error processing data: {str(e)}")
#         else:
#             messages.error(request, "Form is not valid. Please check your inputs.")
#     else:
#         form = QuestionnaireassignForm()

#     context = {
#         'form': form,
#         'page_title': 'Assign Questionnaires'
#     }
#     return render(request, 'hod_template/assign_questionnaire_template.html', context)

# def assign_questionnaire(request):
#     if request.method == 'POST':
#         form = QuestionnaireassignForm(request.POST)
#         if form.is_valid():
#             selected_merchants = form.cleaned_data.get('merchant', [])
#             selected_questionnaires = form.cleaned_data.get('name', [])

#             try:
#                 for questionnaire in selected_questionnaires:
#                     for merchant in selected_merchants:
#                         # Check if a record with the same 'q_id' already exists
#                         if not QuestionnaireMerchant.objects.filter(q_id=questionnaire.q_id, merchant=merchant).exists():
#                             # Create a new instance of the main_app_questionnaire_merchant model
#                             questionnaire_merchant = QuestionnaireMerchant(
#                                 questionnaire=questionnaire,
#                                 merchant=merchant,
#                                 q_id=questionnaire.q_id  # Set the 'q_id' field
#                             )
#                             questionnaire_merchant.save()

#                 messages.success(request, "Successfully Added")
#                 return redirect('assign_questionnaire')
#             except Exception as e:
#                 messages.error(request, f"Error processing data: {str(e)}")
#         else:
#             messages.error(request, "Form is not valid. Please check your inputs.")
#     else:
#         form = QuestionnaireassignForm()

#     context = {
#         'form': form,
#         'page_title': 'Assign Questionnaires'
#     }
#     return render(request, 'hod_template/assign_questionnaire_template.html', context)          

def assign_questionnaire(request):
    if request.method == 'POST':
        form = QuestionnaireassignForm(request.POST)
        
        if form.is_valid():
            print(form.is_valid())
            selected_merchants = form.cleaned_data.get('merchant', [])
            selected_questionnaires = form.cleaned_data.get('name', [])
            
            try:
                
                for questionnaire in selected_questionnaires:
                    for merchant in selected_merchants:
                        # Check if a record with the same 'q_id' already exists
                        if not QuestionnaireMerchant.objects.filter(q_id=questionnaire.q_id, merchant=merchant).exists():
                            # Create a new instance of the main_app_questionnaire_merchant model
                            questionnaire10_merchant = QuestionnaireMerchant(
                                questionnaire=questionnaire,
                                merchant=merchant,
                                q_id=questionnaire.q_id  # Set the 'q_id' field
                            )
                            questionnaire10_merchant.save()

                messages.success(request, "Successfully Added")
                return redirect('assign_questionnaire')
            except Exception as e:
                messages.error(request, f"Error processing data: {str(e)}")
        else:
            messages.error(request, "Form is not valid. Please check your inputs.")
    else:
        form = QuestionnaireassignForm()

    context = {
        'form': form,
        'page_title': 'Assign Questionnaires'
    }
    return render(request, 'hod_template/assign_questionnaire_template.html', context)

def manage_provider(request):
    allProvider = CustomUser.objects.filter(user_type=2)
    context = {
        'allProvider': allProvider,
        'page_title': 'Manage Providers'
    }
    return render(request, "hod_template/manage_provider.html", context)

def manage_response(request):
    allStaff = CustomUser.objects.filter(user_type=2)
    context = {
        'allStaff': allStaff,
        'page_title': 'Manage Response'
    }
    return render(request, "hod_template/manage_provider.html", context)

def manage_merchant(request):
    merchants = CustomUser.objects.filter(user_type=3)
    context = {
        'merchants': merchants,
        'page_title': 'Manage Merchant'
    }
    return render(request, "hod_template/manage_merchant.html", context)


def manage_compliance(request):
    courses = Compliance.objects.all()
    context = {
        'courses': courses,
        'page_title': 'Manage Compliances'
    }
    return render(request, "hod_template/manage_compliance.html", context)


def manage_questionnaire(request):
    unique_q_ids = Questionnaire.objects.values('q_id').distinct()

    # Create an empty list to store the first occurrence of each unique 'q_id'
    first_occurrences = []

    for q_id in unique_q_ids:
        
        first_occurrence = Questionnaire.objects.filter(q_id=q_id['q_id']).first()
        if first_occurrence:
            first_occurrences.append(first_occurrence)
    
    context = {
        # 'subjects': subjects,
        'subjects': first_occurrences,
        'page_title': 'Manage Questionnaire'
    }
    return render(request, "hod_template/manage_questionnaire.html", context)


def edit_provider(request, provider_id):
    provider = get_object_or_404(Provider, id=provider_id)
    form =ProviderForm(request.POST or None, instance=provider)
    context = {
        'form': form,
        'provider_id': provider_id,
        'page_title': 'Edit Provider'
    }
    if request.method == 'POST':
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            address = form.cleaned_data.get('address')
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            gender = form.cleaned_data.get('gender')
            password = form.cleaned_data.get('password') or None
            course = form.cleaned_data.get('course')
            passport = request.FILES.get('profile_pic') or None
            try:
                user = CustomUser.objects.get(id=provider.admin.id)
                user.username = username
                user.email = email
                if password != None:
                    user.set_password(password)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    user.profile_pic = passport_url
                user.first_name = first_name
                user.last_name = last_name
                user.gender = gender
                user.address = address
                provider.course = course
                user.save()
                provider.save()
                messages.success(request, "Successfully Updated")
                return redirect(reverse('edit_provider', args=[provider_id]))
            except Exception as e:
                messages.error(request, "Could Not Update " + str(e))
        else:
            messages.error(request, "Please fil form properly")
    else:
        user = CustomUser.objects.get(id=provider_id)
        provider = Provider.objects.get(id=user.id)
        return render(request, "hod_template/edit_provider_template.html", context)


def edit_merchant(request, merchant_id):
    merchant = get_object_or_404(Merchant, id=merchant_id)
    form = MerchantForm(request.POST or None, instance=merchant)
    context = {
        'form': form,
        'merchant_id': merchant_id,
        'page_title': 'Edit Merchant'
    }
    if request.method == 'POST':
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            address = form.cleaned_data.get('address')
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            gender = form.cleaned_data.get('gender')
            password = form.cleaned_data.get('password') or None
            course = form.cleaned_data.get('course')
            session = form.cleaned_data.get('session')
            passport = request.FILES.get('profile_pic') or None
            try:
                user = CustomUser.objects.get(id=merchant.admin.id)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    user.profile_pic = passport_url
                user.username = username
                user.email = email
                if password != None:
                    user.set_password(password)
                user.first_name = first_name
                user.last_name = last_name
                merchant.session = session
                user.gender = gender
                user.address = address
                merchant.course = course
                user.save()
                merchant.save()
                messages.success(request, "Successfully Updated")
                return redirect(reverse('edit_merchant', args=[merchant_id]))
            except Exception as e:
                messages.error(request, "Could Not Update " + str(e))
        else:
            messages.error(request, "Please Fill Form Properly!")
    else:
        return render(request, "hod_template/edit_merchant_template.html", context)


def edit_compliance(request, compliance_id):
    instance = get_object_or_404(Compliance, id=compliance_id)
    form = ComplianceForm(request.POST or None, instance=instance)
    context = {
        'form': form,
        'compliance_id': compliance_id,
        'page_title': 'Edit Compliance'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            try:
                course = Compliance.objects.get(id=compliance_id)
                course.name = name
                course.save()
                messages.success(request, "Successfully Updated")
            except:
                messages.error(request, "Could Not Update")
        else:
            messages.error(request, "Could Not Update")

    return render(request, 'hod_template/edit_course_template.html', context)


def edit_questionnaire(request, subject_id):
    instance = get_object_or_404(Questionnaire, id=subject_id)
    form = QuestionnaireForm(request.POST or None, instance=instance)
    context = {
        'form': form,
        'subject_id': subject_id,
        'page_title': 'Edit Subject'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            compliance = form.cleaned_data.get('course')
            provider = form.cleaned_data.get('staff')
            try:
                subject = Questionnaire.objects.get(id=subject_id)
                subject.name = name
                subject.provider = provider
                subject.compliance = compliance
                subject.save()
                messages.success(request, "Successfully Updated")
                return redirect(reverse('edit_questionnaire', args=[subject_id]))
            except Exception as e:
                messages.error(request, "Could Not Add " + str(e))
        else:
            messages.error(request, "Fill Form Properly")
    return render(request, 'hod_template/edit_subject_template.html', context)


def add_session(request):
    form = SessionForm(request.POST or None)
    context = {'form': form, 'page_title': 'Add Session'}
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Session Created")
                return redirect(reverse('add_session'))
            except Exception as e:
                messages.error(request, 'Could Not Add ' + str(e))
        else:
            messages.error(request, 'Fill Form Properly ')
    return render(request, "hod_template/add_session_template.html", context)


def manage_session(request):
    sessions = Session.objects.all()
    context = {'sessions': sessions, 'page_title': 'Manage Sessions'}
    return render(request, "hod_template/manage_session.html", context)


def edit_session(request, session_id):
    instance = get_object_or_404(Session, id=session_id)
    form = SessionForm(request.POST or None, instance=instance)
    context = {'form': form, 'session_id': session_id,
               'page_title': 'Edit Session'}
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Session Updated")
                return redirect(reverse('edit_session', args=[session_id]))
            except Exception as e:
                messages.error(
                    request, "Session Could Not Be Updated " + str(e))
                return render(request, "hod_template/edit_session_template.html", context)
        else:
            messages.error(request, "Invalid Form Submitted ")
            return render(request, "hod_template/edit_session_template.html", context)

    else:
        return render(request, "hod_template/edit_session_template.html", context)


@csrf_exempt
def check_email_availability(request):
    email = request.POST.get("email")
    try:
        user = CustomUser.objects.filter(email=email).exists()
        if user:
            return HttpResponse(True)
        return HttpResponse(False)
    except Exception as e:
        return HttpResponse(False)


@csrf_exempt
def merchant_feedback_message(request):
    if request.method != 'POST':
        feedbacks = FeedbackStudent.objects.all()
        context = {
            'feedbacks': feedbacks,
            'page_title': 'Student Feedback Messages'
        }
        return render(request, 'hod_template/merchant_feedback_template.html', context)
    else:
        feedback_id = request.POST.get('id')
        try:
            feedback = get_object_or_404(FeedbackStudent, id=feedback_id)
            reply = request.POST.get('reply')
            feedback.reply = reply
            feedback.save()
            return HttpResponse(True)
        except Exception as e:
            return HttpResponse(False)


@csrf_exempt
def provider_feedback_message(request):
    if request.method != 'POST':
        feedbacks = FeedbackStaff.objects.all()
        context = {
            'feedbacks': feedbacks,
            'page_title': 'Staff Feedback Messages'
        }
        return render(request, 'hod_template/provider_feedback_template.html', context)
    else:
        feedback_id = request.POST.get('id')
        try:
            feedback = get_object_or_404(FeedbackStaff, id=feedback_id)
            reply = request.POST.get('reply')
            feedback.reply = reply
            feedback.save()
            return HttpResponse(True)
        except Exception as e:
            return HttpResponse(False)


@csrf_exempt
def view_staff_leave(request):
    if request.method != 'POST':
        allLeave = LeaveReportStaff.objects.all()
        context = {
            'allLeave': allLeave,
            'page_title': 'Leave Applications From Staff'
        }
        return render(request, "hod_template/staff_leave_view.html", context)
    else:
        id = request.POST.get('id')
        status = request.POST.get('status')
        if (status == '1'):
            status = 1
        else:
            status = -1
        try:
            leave = get_object_or_404(LeaveReportStaff, id=id)
            leave.status = status
            leave.save()
            return HttpResponse(True)
        except Exception as e:
            return False


@csrf_exempt
def view_student_leave(request):
    if request.method != 'POST':
        allLeave = LeaveReportStudent.objects.all()
        context = {
            'allLeave': allLeave,
            'page_title': 'Leave Applications From Students'
        }
        return render(request, "hod_template/student_leave_view.html", context)
    else:
        id = request.POST.get('id')
        status = request.POST.get('status')
        if (status == '1'):
            status = 1
        else:
            status = -1
        try:
            leave = get_object_or_404(LeaveReportStudent, id=id)
            leave.status = status
            leave.save()
            return HttpResponse(True)
        except Exception as e:
            return False


def admin_view_attendance(request):
    subjects = Questionnaire.objects.all()
    sessions = Session.objects.all()
    context = {
        'subjects': subjects,
        'sessions': sessions,
        'page_title': 'View Attendance'
    }

    return render(request, "hod_template/admin_view_attendance.html", context)


@csrf_exempt
def get_admin_attendance(request):
    subject_id = request.POST.get('subject')
    session_id = request.POST.get('session')
    attendance_date_id = request.POST.get('attendance_date_id')
    try:
        subject = get_object_or_404(Questionnaire, id=subject_id)
        session = get_object_or_404(Session, id=session_id)
        attendance = get_object_or_404(
            Attendance, id=attendance_date_id, session=session)
        attendance_reports = AttendanceReport.objects.filter(
            attendance=attendance)
        json_data = []
        for report in attendance_reports:
            data = {
                "status":  str(report.status),
                "name": str(report.student)
            }
            json_data.append(data)
        return JsonResponse(json.dumps(json_data), safe=False)
    except Exception as e:
        return None


def admin_view_profile(request):
    admin = get_object_or_404(Admin, admin=request.user)
    form = AdminForm(request.POST or None, request.FILES or None,
                     instance=admin)
    context = {'form': form,
               'page_title': 'View/Edit Profile'
               }
    if request.method == 'POST':
        try:
            if form.is_valid():
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                password = form.cleaned_data.get('password') or None
                passport = request.FILES.get('profile_pic') or None
                custom_user = admin.admin
                if password != None:
                    custom_user.set_password(password)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    custom_user.profile_pic = passport_url
                custom_user.first_name = first_name
                custom_user.last_name = last_name
                custom_user.save()
                messages.success(request, "Profile Updated!")
                return redirect(reverse('admin_view_profile'))
            else:
                messages.error(request, "Invalid Data Provided")
        except Exception as e:
            messages.error(
                request, "Error Occured While Updating Profile " + str(e))
    return render(request, "hod_template/admin_view_profile.html", context)


def admin_notify_provider(request):
    provider = CustomUser.objects.filter(user_type=2)
    context = {
        'page_title': "Send Notifications To Provider",
        'allPovider': provider
    }
    return render(request, "hod_template/provider_notification.html", context)


def admin_notify_merchant(request):
    merchant = CustomUser.objects.filter(user_type=3)
    context = {
        'page_title': "Send Notifications To Merchant",
        'merchants': merchant
    }
    return render(request, "hod_template/merchant_notification.html", context)


@csrf_exempt
def send_merchant_notification(request):
    id = request.POST.get('id')
    message = request.POST.get('message')
    student = get_object_or_404(Merchant, admin_id=id)
    try:
        url = "https://fcm.googleapis.com/fcm/send"
        body = {
            'notification': {
                'title': "Student Management System",
                'body': message,
                'click_action': reverse('merchant_view_notification'),
                'icon': static('dist/img/AdminLTELogo.png')
            },
            'to': student.admin.fcm_token
        }
        headers = {'Authorization':
                   'key=AAAA3Bm8j_M:APA91bElZlOLetwV696SoEtgzpJr2qbxBfxVBfDWFiopBWzfCfzQp2nRyC7_A2mlukZEHV4g1AmyC6P_HonvSkY2YyliKt5tT3fe_1lrKod2Daigzhb2xnYQMxUWjCAIQcUexAMPZePB',
                   'Content-Type': 'application/json'}
        data = requests.post(url, data=json.dumps(body), headers=headers)
        notification = NotificationMerchant(student=student, message=message)
        notification.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


@csrf_exempt
def send_provider_notification(request):
    id = request.POST.get('id')
    message = request.POST.get('message')
    provider = get_object_or_404(Provider, admin_id=id)
    try:
        url = "https://fcm.googleapis.com/fcm/send"
        body = {
            'notification': {
                'title': "Student Management System",
                'body': message,
                'click_action': reverse('provider_view_notification'),
                'icon': static('dist/img/AdminLTELogo.png')
            },
            'to': provider.admin.fcm_token
        }
        headers = {'Authorization':
                   'key=AAAA3Bm8j_M:APA91bElZlOLetwV696SoEtgzpJr2qbxBfxVBfDWFiopBWzfCfzQp2nRyC7_A2mlukZEHV4g1AmyC6P_HonvSkY2YyliKt5tT3fe_1lrKod2Daigzhb2xnYQMxUWjCAIQcUexAMPZePB',
                   'Content-Type': 'application/json'}
        data = requests.post(url, data=json.dumps(body), headers=headers)
        notification = NotificationProvider(staff=provider, message=message)
        notification.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


def delete_provider(request, staff_id):
    provider = get_object_or_404(CustomUser, provider__id=staff_id)
    provider.delete()
    messages.success(request, "Provider deleted successfully!")
    return redirect(reverse('manage_provider'))


def delete_merchant(request, merchant_id):
    merchant = get_object_or_404(CustomUser, merchant__id=merchant_id)
    merchant.delete()
    messages.success(request, "Merchant deleted successfully!")
    return redirect(reverse('manage_merchant'))


def delete_compliance(request, compliance_id):
    course = get_object_or_404(Compliance, id=compliance_id)
    try:
        course.delete()
        messages.success(request, "Course deleted successfully!")
    except Exception:
        messages.error(
            request, "Sorry, some students are assigned to this course already. Kindly change the affected student course and try again")
    return redirect(reverse('manage_compliance'))


def delete_questionnaire(request, subject_id):
    subject = get_object_or_404(Questionnaire, id=subject_id)
    subject.delete()
    messages.success(request, "Questionnaire deleted successfully!")
    return redirect(reverse('manage_questionnaire'))


def delete_session(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    try:
        session.delete()
        messages.success(request, "Session deleted successfully!")
    except Exception:
        messages.error(
            request, "There are students assigned to this session. Please move them to another session.")
    return redirect(reverse('manage_session'))
