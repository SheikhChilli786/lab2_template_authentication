from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .models import Course, Lesson, Enrollment
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.http import Http404
from django.urls import reverse
from django.views import generic, View
from collections import defaultdict
from django.contrib.auth import login, logout, authenticate
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)

# Create authentication related views
def logout_request(request):
    # Get the user object based on session id in request
    print("Log out the user `{}`".format(request.user.username))
    # Logout user in the request
    logout(request)
    # Redirect user back to course list view
    return redirect('onlinecourse:popular_course_list')


# Add a class-based course list view
class CourseListView(generic.ListView):
    template_name = 'onlinecourse/course_list.html'
    context_object_name = 'course_list'

    def get_queryset(self):
       courses = Course.objects.order_by('-total_enrollment')[:10]
       return courses


# Add a generic course details view
class CourseDetailsView(generic.DetailView):
    model = Course
    template_name = 'onlinecourse/course_detail.html'


class EnrollView(View):

    # Handles get request
    def post(self, request, *args, **kwargs):
        course_id = kwargs.get('pk')
        course = get_object_or_404(Course, pk=course_id)
        # Create an enrollment
        course.total_enrollment += 1
        course.save()
        return HttpResponseRedirect(reverse(viewname='onlinecourse:course_details', args=(course.id,)))

def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["psw"]

        user = authenticate(username = username,password = password)
        if user is not None:
            login(request,user)
            return redirect('onlinecourse:popular_course_list')
        else:
            return render(request, 'onlinecourse/user_login.html',context)
    else:
        return render(request,'onlinecourse/user_login.html',context)

def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'onlinecourse/user_registration.html',context)
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.debug("{} is new user".format(username))

        if not user_exist:
            user = User.objects.create_user(username = username,password = password)
            login(request,user)
            return redirect("onlinecourse:popular_course_list")
        else:
            return render(request,'onlinecourse/user_registration.html',context)