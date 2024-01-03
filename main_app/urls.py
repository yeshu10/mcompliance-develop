"""college_management_system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from main_app.EditResultView import EditResultView

from . import hod_views, staff_views, student_views, views

urlpatterns = [
    
    path("", views.login_page, name='login_page'),
    path("get_attendance", views.get_attendance, name='get_attendance'),
    path("firebase-messaging-sw.js", views.showFirebaseJS, name='showFirebaseJS'),
    path("doLogin/", views.doLogin, name='user_login'),
    path("logout_user/", views.logout_user, name='user_logout'),
    path("admin/home/", hod_views.admin_home, name='admin_home'),
    path("provider/add/", hod_views.add_provider, name='add_provider'),
    path("compliance/add", hod_views.add_compliance, name='add_compliance'),
    path("send_merchant_notification/", hod_views.send_merchant_notification,
         name='send_merchant_notification'),
    path("send_provider_notification/", hod_views.send_provider_notification,
         name='send_provider_notification'),
    path("add_session/", hod_views.add_session, name='add_session'),
    path("admin_notify_merchant", hod_views.admin_notify_merchant,
         name='admin_notify_merchant'),
    path("admin_notify_provider", hod_views.admin_notify_provider,
         name='admin_notify_provider'),
    path("admin_view_profile", hod_views.admin_view_profile,
         name='admin_view_profile'),
    path("check_email_availability", hod_views.check_email_availability,
         name="check_email_availability"),
    path("session/manage/", hod_views.manage_session, name='manage_session'),
    path("session/edit/<int:session_id>",
         hod_views.edit_session, name='edit_session'),
    path("student/view/feedback/", hod_views.merchant_feedback_message,
         name="merchant_feedback_message",),
    path("staff/view/feedback/", hod_views.provider_feedback_message,
         name="provider_feedback_message",),
    path("student/view/leave/", hod_views.view_student_leave,
         name="view_student_leave",),
    path("staff/view/leave/", hod_views.view_staff_leave, name="view_staff_leave",),
    path("attendance/view/", hod_views.admin_view_attendance,
         name="admin_view_attendance",),
    path("attendance/fetch/", hod_views.get_admin_attendance,
         name='get_admin_attendance'),
    path("merchant/add/", hod_views.add_merchant, name='add_merchant'),
    path("questionnaire/add/", hod_views.add_questionnaire, name='add_questionnaire'),
    path("questionnaire/asssign/", hod_views.assign_questionnaire, name='assign_questionnaire'),
    path("response/manage/", hod_views.manage_response, name='manage_response'),
    path("provider/manage/", hod_views.manage_provider, name='manage_provider'),
    path("merchant/manage/", hod_views.manage_merchant, name='manage_merchant'),
    
    path("compliance/manage/", hod_views.manage_compliance, name='manage_compliance'),
    path("questionnaire/manage/", hod_views.manage_questionnaire, name='manage_questionnaire'),
    path("provider/edit/<int:provider_id>", hod_views.edit_provider, name='edit_provider'),
    path("provider/delete/<int:provider_id>",
         hod_views.delete_provider, name='delete_provider'),

    path("compliance/delete/<int:compliance_id>",
         hod_views.delete_compliance, name='delete_compliance'),

    path("questionnaire/delete/<int:subject_id>",
         hod_views.delete_questionnaire, name='delete_questionnaire'),

    path("session/delete/<int:session_id>",
         hod_views.delete_session, name='delete_session'),

    path("merchant/delete/<int:merchant_id>",
         hod_views.delete_merchant, name='delete_merchant'),
    path("merchant/edit/<int:merchant_id>",
         hod_views.edit_merchant, name='edit_merchant'),
    path("compliance/edit/<int:compliance_id>",
         hod_views.edit_compliance, name='edit_compliance'),
    path("questionnaire/edit/<int:subject_id>",
         hod_views.edit_questionnaire, name='edit_questionnaire'),


    # Staff
    path("provider/home/", staff_views.provider_home, name='provider_home'),
    path("provider/apply/leave/", staff_views.provider_apply_leave,
         name='provider_apply_leave'),
    path("provider/feedback/", staff_views.provider_feedback, name='provider_feedback'),
    path("provider/view/profile/", staff_views.provider_view_profile,
         name='provider_view_profile'),
    path("staff/attendance/take/", staff_views.staff_take_attendance,
         name='staff_take_attendance'),
    path("staff/attendance/update/", staff_views.staff_update_attendance,
         name='staff_update_attendance'),
    path("staff/get_students/", staff_views.get_students, name='get_students'),
     path("staff/addbook/", staff_views.add_book, name="add_book"),
    path("staff/issue_book/", staff_views.issue_book, name="issue_book"),
    path("staff/view_issued_book/", staff_views.view_issued_book, name="view_issued_book"),



    path("staff/attendance/fetch/", staff_views.get_student_attendance,
         name='get_student_attendance'),
    path("staff/attendance/save/",
         staff_views.save_attendance, name='save_attendance'),
    path("staff/attendance/update/",
         staff_views.update_attendance, name='update_attendance'),
    path("staff/fcmtoken/", staff_views.staff_fcmtoken, name='staff_fcmtoken'),
    path("provider/view/notification/", staff_views.provider_view_notification,
         name="provider_view_notification"),
    path("provider/view/compliance/", staff_views.provider_view_compliance,
         name="provider_view_compliance"),
    path("provider/available/compliance/", staff_views.provider_available_compliance,
                    name="provider_available_compliance"),   
    path("staff/result/add/", staff_views.staff_add_result, name='staff_add_result'),
    path("staff/result/edit/", EditResultView.as_view(),
         name='edit_student_result'),
    path('staff/result/fetch/', staff_views.fetch_student_result,
         name='fetch_student_result'),



    # Student
    path("merchant/home/", student_views.merchant_home, name='merchant_home'),
    path("merchant/view/attendance/", student_views.merchant_view_attendance,
         name='merchant_view_attendance'),
    path("merchant/apply/leave/", student_views.merchant_apply_leave,
         name='merchant_apply_leave'),
    path("merchant/feedback/", student_views.merchant_feedback,
         name='merchant_feedback'),
    path("merchant/view/profile/", student_views.merchant_view_profile,
         name='merchant_view_profile'),
    path("student/fcmtoken/", student_views.student_fcmtoken,
         name='student_fcmtoken'),
     # path('student/todo',student_views.todo,name='todo'),

     
     path("student/viewbooks/", student_views.view_books, name="view_books"),

    path("merchant/view/notification/", student_views.merchant_view_notification,
         name="merchant_view_notification"),
    path("merchant/view/compliance/", student_views.merchant_view_compliance,
         name="merchant_view_compliance"),     
    path("merchant/assigned/compliance/", student_views.merchant_assigned_compliance,
         name="merchant_assigned_compliance"),
    path("submit/responses", student_views.submit_responses,
         name="submit_responses"),   
    path("edited/responses", student_views.edited_responses,
         name="edited_responses"),        
    path('student/view/result/', student_views.student_view_result,
         name='student_view_result'),
    path('merchant/create/form/<int:q_id>/', student_views.merchant_create_form,
         name='merchant_create_form'),
    path('merchant/view/response/<int:q_id>/', student_views.merchant_view_response,
         name='merchant_view_response'),   
    path('merchant/edit/response/<int:q_id>/', student_views.merchant_edit_response,
         name='merchant_edit_response'),    

]
