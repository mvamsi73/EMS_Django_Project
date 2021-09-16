from datetime import datetime, date

from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from django.core.mail import send_mail
from .utils import get_pie_plot,courses_bar_chart,attendance_pie_chart,quiz_analytics_bar,quiz_analytics_filter_bar
# from .models import *
# from .forms import *

def home_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'school/index.html')



#for showing signup/login button for admin
def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'school/adminclick.html')


#for showing signup/login button for teacher
def teacherclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'school/teacherclick.html')


#for showing signup/login button for student
def studentclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'school/studentclick.html')





def admin_signup_view(request):
    form=forms.AdminSigupForm()
    if request.method=='POST':
        form=forms.AdminSigupForm(request.POST)
        if form.is_valid():
            user=form.save()
            user.set_password(user.password)
            user.save()


            my_admin_group = Group.objects.get_or_create(name='ADMIN')
            my_admin_group[0].user_set.add(user)

            return HttpResponseRedirect('adminlogin')
    return render(request,'school/adminsignup.html',{'form':form})




def student_signup_view(request):
    form1=forms.StudentUserForm()
    form2=forms.StudentExtraForm()
    mydict={'form1':form1,'form2':form2}
    if request.method=='POST':
        form1=forms.StudentUserForm(request.POST)
        form2=forms.StudentExtraForm(request.POST)
        if form1.is_valid() and form2.is_valid():
            user=form1.save()
            user.set_password(user.password)
            user.save()
            f2=form2.save(commit=False)
            f2.user=user
            user2=f2.save()

            my_student_group = Group.objects.get_or_create(name='STUDENT')
            my_student_group[0].user_set.add(user)

        return HttpResponseRedirect('studentlogin')
    return render(request,'school/studentsignup.html',context=mydict)


def teacher_signup_view(request):
    form1=forms.TeacherUserForm()
    form2=forms.TeacherExtraForm()
    mydict={'form1':form1,'form2':form2}
    if request.method=='POST':
        form1=forms.TeacherUserForm(request.POST)
        form2=forms.TeacherExtraForm(request.POST)
        if form1.is_valid() and form2.is_valid():
            user=form1.save()
            user.set_password(user.password)
            user.save()
            f2=form2.save(commit=False)
            f2.user=user
            user2=f2.save()

            my_teacher_group = Group.objects.get_or_create(name='TEACHER')
            my_teacher_group[0].user_set.add(user)

        return HttpResponseRedirect('teacherlogin')
    return render(request,'school/teachersignup.html',context=mydict)






#for checking user is techer , student or admin
def is_admin(user):
    return user.groups.filter(name='ADMIN').exists()
def is_teacher(user):
    return user.groups.filter(name='TEACHER').exists()
def is_student(user):
    return user.groups.filter(name='STUDENT').exists()


def afterlogin_view(request):
    if is_admin(request.user):
        return redirect('admin-dashboard')
    elif is_teacher(request.user):
        accountapproval=models.TeacherExtra.objects.all().filter(user_id=request.user.id,status=True)
        if accountapproval:
            return redirect('teacher-dashboard')
        else:
            return render(request,'school/teacher_wait_for_approval.html')
    elif is_student(request.user):
        accountapproval=models.StudentExtra.objects.all().filter(user_id=request.user.id,status=True)
        if accountapproval:
            return redirect('student-dashboard')
        else:
            return render(request,'school/student_wait_for_approval.html')




#for dashboard of admin

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_dashboard_view(request):
    teachercount=models.TeacherExtra.objects.all().filter(status=True).count()
    pendingteachercount=models.TeacherExtra.objects.all().filter(status=False).count()

    studentcount=models.StudentExtra.objects.all().filter(status=True).count()
    pendingstudentcount=models.StudentExtra.objects.all().filter(status=False).count()

    teachersalary=models.TeacherExtra.objects.filter(status=True).aggregate(Sum('salary'))
    pendingteachersalary=models.TeacherExtra.objects.filter(status=False).aggregate(Sum('salary'))

    studentfee=models.StudentExtra.objects.filter(status=True).aggregate(Sum('fee',default=0))
    pendingstudentfee=models.StudentExtra.objects.filter(status=False).aggregate(Sum('fee'))

    notice=models.Notice.objects.all()

    # plotting graphes
    # 1.plotting studentcount vs teachercount (piechart)
    labels=['TOTAL FACULTY COUNT','TOTAL STUDENT COUNT']
    stucnt_vs_faccnt_pie=get_pie_plot([teachercount,studentcount],labels,'Faculty Count VS Student Count')

    # 2.Number of students enrolled in different courses bar graph
    courses=models.courses.objects.all()
    coursenames=[i.coursename for i in courses]
    ids=[i.id for i in courses]
    values=[]
    for i in ids:
        student_courses=models.student_registered_courses.objects.all().filter(courseid=i,status='Registered')
        values.append(len(student_courses))
    stu_reg_in_courses=courses_bar_chart(coursenames,values,'Students')

    # 3. Number of teachers registered in each course
    values=[]
    for i in ids:
        teacher_courses=models.teacher_registered_courses.objects.all().filter(course_id=i)
        values.append(len(teacher_courses))
    teacher_reg_in_courses=courses_bar_chart(coursenames,values,'Teachers')

    # 4.Probability of Students attending classes
    values=[]
    attendance=models.Attendance.objects.all()
    dates=[i.date for i in attendance]
    dates=list(set(dates))
    for j in dates:
        c=0
        for i in attendance:
            if(i.date==j and i.present_status=='Present'):
                c+=1
        values.append(c)
    avg_attendance=get_pie_plot([((len(values)-values.count(0))/len(attendance)),1-((len(values)-values.count(0))/len(attendance))],['Probablility of Attending','Probablility of not attending'],'Probability of Students attending classes')

    # 5. Attendence pie chart
    lst=[]
    for i in range(len(dates)):
        lst.append(str(dates[i]))
    attendance_pie=attendance_pie_chart(lst,values)


    #aggregate function return dictionary so fetch data from dictionary
    mydict={
        'teachercount':teachercount,
        'pendingteachercount':pendingteachercount,

        'studentcount':studentcount,
        'pendingstudentcount':pendingstudentcount,

        'teachersalary':teachersalary['salary__sum'],
        'pendingteachersalary':pendingteachersalary['salary__sum'],

        'studentfee':studentfee['fee__sum'],
        'pendingstudentfee':pendingstudentfee['fee__sum'],

        'notice':notice,
        'stucnt_vs_faccnt_pie':stucnt_vs_faccnt_pie,
        'stu_reg_in_courses':stu_reg_in_courses,
        'teacher_reg_in_courses':teacher_reg_in_courses,
        'avg_attendance':avg_attendance,
        'attendance_pie_chart':attendance_pie
    }

    return render(request,'school/admin_dashboard_new.html',context=mydict)


#for teacher section by admin

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_teacher_view(request):
    return render(request,'school/admin_teacher.html')

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_add_teacher_view(request):
    form1=forms.TeacherUserForm()
    form2=forms.TeacherExtraForm()
    mydict={'form1':form1,'form2':form2}
    if request.method=='POST':
        form1=forms.TeacherUserForm(request.POST)
        form2=forms.TeacherExtraForm(request.POST)
        if form1.is_valid() and form2.is_valid():
            user=form1.save()
            user.set_password(user.password)
            user.save()

            f2=form2.save(commit=False)
            f2.user=user
            f2.status=True
            f2.save()

            my_teacher_group = Group.objects.get_or_create(name='TEACHER')
            my_teacher_group[0].user_set.add(user)

        return HttpResponseRedirect('admin-teacher')
    return render(request,'school/admin_add_teacher.html',context=mydict)


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_teacher_view(request):
    teachers=models.TeacherExtra.objects.all().filter(status=True)
    return render(request,'school/admin_view_teacher.html',{'teachers':teachers})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_approve_teacher_view(request):
    teachers=models.TeacherExtra.objects.all().filter(status=False)
    return render(request,'school/admin_approve_teacher.html',{'teachers':teachers})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def approve_teacher_view(request,pk):
    teacher=models.TeacherExtra.objects.get(id=pk)
    teacher.status=True
    teacher.save()
    return redirect(reverse('admin-approve-teacher'))


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def delete_teacher_view(request,pk):
    teacher=models.TeacherExtra.objects.get(id=pk)
    user=models.User.objects.get(id=teacher.user_id)
    user.delete()
    teacher.delete()
    return redirect('admin-approve-teacher')


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def delete_teacher_from_school_view(request,pk):
    teacher=models.TeacherExtra.objects.get(id=pk)
    user=models.User.objects.get(id=teacher.user_id)
    user.delete()
    teacher.delete()
    return redirect('admin-view-teacher')


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def update_teacher_view(request,pk):
    teacher=models.TeacherExtra.objects.get(id=pk)
    user=models.User.objects.get(id=teacher.user_id)

    form1=forms.TeacherUserForm(instance=user)
    form2=forms.TeacherExtraForm(instance=teacher)
    mydict={'form1':form1,'form2':form2}

    if request.method=='POST':
        form1=forms.TeacherUserForm(request.POST,instance=user)
        form2=forms.TeacherExtraForm(request.POST,instance=teacher)
        print(form1)
        if form1.is_valid() and form2.is_valid():
            user=form1.save()
            user.set_password(user.password)
            user.save()
            f2=form2.save(commit=False)
            f2.status=True
            f2.save()
            return redirect('admin-view-teacher')
    return render(request,'school/admin_update_teacher.html',context=mydict)


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_teacher_salary_view(request):
    teachers=models.TeacherExtra.objects.all()
    return render(request,'school/admin_view_teacher_salary.html',{'teachers':teachers})





@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_student_view(request):
    return render(request,'school/admin_student.html')


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_add_student_view(request):
    form1=forms.StudentUserForm()
    form2=forms.StudentExtraForm()
    mydict={'form1':form1,'form2':form2}
    if request.method=='POST':
        form1=forms.StudentUserForm(request.POST)
        form2=forms.StudentExtraForm(request.POST)
        if form1.is_valid() and form2.is_valid():
            print("form is valid")
            user=form1.save()
            user.set_password(user.password)
            user.save()

            f2=form2.save(commit=False)
            f2.user=user
            f2.status=True
            f2.save()

            my_student_group = Group.objects.get_or_create(name='STUDENT')
            my_student_group[0].user_set.add(user)
        else:
            print("form is invalid")
        return HttpResponseRedirect('admin-student')
    return render(request,'school/admin_add_student.html',context=mydict)


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_student_view(request):
    students=models.StudentExtra.objects.all().filter(status=True)
    return render(request,'school/admin_view_student.html',{'students':students})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def delete_student_from_school_view(request,pk):
    student=models.StudentExtra.objects.get(id=pk)
    user=models.User.objects.get(id=student.user_id)
    user.delete()
    student.delete()
    return redirect('admin-view-student')

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def delete_course(request,id):
    course=models.courses.objects.get(id=id)
    course.delete()
    models.student_registered_courses.objects.filter(courseid=id).delete()

    return redirect('admin_add_course')

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def delete_student_view(request,pk):
    student=models.StudentExtra.objects.get(id=pk)
    user=models.User.objects.get(id=student.user_id)
    user.delete()
    student.delete()
    return redirect('admin-approve-student')


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def update_student_view(request,pk):
    student=models.StudentExtra.objects.get(id=pk)
    user=models.User.objects.get(id=student.user_id)
    form1=forms.StudentUserForm(instance=user)
    form2=forms.StudentExtraForm(instance=student)
    mydict={'form1':form1,'form2':form2}
    if request.method=='POST':
        form1=forms.StudentUserForm(request.POST,instance=user)
        form2=forms.StudentExtraForm(request.POST,instance=student)
        print(form1)
        if form1.is_valid() and form2.is_valid():
            user=form1.save()
            user.set_password(user.password)
            user.save()
            f2=form2.save(commit=False)
            f2.status=True
            f2.save()
            return redirect('admin-view-student')
    return render(request,'school/admin_update_student.html',context=mydict)



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_approve_student_view(request):
    students=models.StudentExtra.objects.all().filter(status=False)
    return render(request,'school/admin_approve_student.html',{'students':students})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def approve_student_view(request,pk):
    students=models.StudentExtra.objects.get(id=pk)
    students.status=True
    students.save()
    return redirect(reverse('admin-approve-student'))


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_student_fee_view(request):
    students=models.StudentExtra.objects.all()
    return render(request,'school/admin_view_student_fee.html',{'students':students})






#attendance related view
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_attendance_view(request):
    return render(request,'school/admin_attendance.html')


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_take_attendance_view(request,cl):
    students=models.StudentExtra.objects.all().filter(cl=cl)
    print(students)
    aform=forms.AttendanceForm()
    if request.method=='POST':
        form=forms.AttendanceForm(request.POST)
        if form.is_valid():
            Attendances=request.POST.getlist('present_status')
            date=form.cleaned_data['date']
            for i in range(len(Attendances)):
                AttendanceModel=models.Attendance()
                AttendanceModel.cl=cl
                AttendanceModel.date=date
                AttendanceModel.present_status=Attendances[i]
                AttendanceModel.roll=students[i].roll
                AttendanceModel.save()
            return redirect('admin-attendance')
        else:
            print('form invalid')
    return render(request,'school/admin_take_attendance.html',{'students':students,'aform':aform})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_attendance_view(request,cl):
    form=forms.AskDateForm()
    if request.method=='POST':
        form=forms.AskDateForm(request.POST)
        if form.is_valid():
            date=form.cleaned_data['date']
            attendancedata=models.Attendance.objects.all().filter(date=date,cl=cl)
            studentdata=models.StudentExtra.objects.all().filter(cl=cl)
            mylist=zip(attendancedata,studentdata)
            return render(request,'school/admin_view_attendance_page.html',{'cl':cl,'mylist':mylist,'date':date})
        else:
            print('form invalid')
    return render(request,'school/admin_view_attendance_ask_date.html',{'cl':cl,'form':form})









#fee related view by admin
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_fee_view(request):
    return render(request,'school/admin_fee.html')


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_fee_view(request,cl):
    feedetails=models.StudentExtra.objects.all().filter(cl=cl)
    return render(request,'school/admin_view_fee.html',{'feedetails':feedetails,'cl':cl})








#notice related views
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_notice_view(request):
    form=forms.NoticeForm()
    if request.method=='POST':
        form=forms.NoticeForm(request.POST)
        if form.is_valid():
            form=form.save(commit=False)
            form.by=request.user.first_name
            form.save()
            return redirect('admin-dashboard')
    return render(request,'school/admin_notice.html',{'form':form})








#for TEACHER  LOGIN    SECTION
@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_dashboard_view(request):
    teacherdata=models.TeacherExtra.objects.all().filter(status=True,user_id=request.user.id)
    notice=models.Notice.objects.all()
    mydict={
        'salary':teacherdata[0].salary,
        'mobile':teacherdata[0].mobile,
        'date':teacherdata[0].joindate,
        'notice':notice
    }
    return render(request,'school/teacher_dashboard_new.html',context=mydict)



@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_attendance_view(request):
    return render(request,'school/teacher_attendance.html')


@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_take_attendance_view(request,cl):
    students=models.StudentExtra.objects.all().filter(cl=cl)
    aform=forms.AttendanceForm()
    if request.method=='POST':
        form=forms.AttendanceForm(request.POST)
        if form.is_valid():
            Attendances=request.POST.getlist('present_status')
            date=form.cleaned_data['date']
            for i in range(len(Attendances)):
                AttendanceModel=models.Attendance()
                AttendanceModel.cl=cl
                AttendanceModel.date=date
                AttendanceModel.present_status=Attendances[i]
                AttendanceModel.roll=students[i].roll
                AttendanceModel.save()
            return redirect('teacher-attendance')
        else:
            print('form invalid')
    return render(request,'school/teacher_take_attendance.html',{'students':students,'aform':aform})



@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_view_attendance_view(request,cl):
    form=forms.AskDateForm()
    if request.method=='POST':
        form=forms.AskDateForm(request.POST)
        if form.is_valid():
            date=form.cleaned_data['date']
            attendancedata=models.Attendance.objects.all().filter(date=date,cl=cl)
            studentdata=models.StudentExtra.objects.all().filter(cl=cl)
            mylist=zip(attendancedata,studentdata)
            return render(request,'school/teacher_view_attendance_page.html',{'cl':cl,'mylist':mylist,'date':date})
        else:
            print('form invalid')
    return render(request,'school/teacher_view_attendance_ask_date.html',{'cl':cl,'form':form})



@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_notice_view(request):
    form=forms.NoticeForm()
    if request.method=='POST':
        form=forms.NoticeForm(request.POST)
        if form.is_valid():
            form=form.save(commit=False)
            form.by=request.user.first_name
            form.save()
            return redirect('teacher-dashboard')
        else:
            print('form invalid')
    return render(request,'school/teacher_notice.html',{'form':form})







#FOR STUDENT AFTER THEIR Login(by sumit)
@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_dashboard_view(request):
    studentdata=models.StudentExtra.objects.all().filter(status=True,user_id=request.user.id)
    notice=models.Notice.objects.all()
    mydict={
        'roll':studentdata[0].roll,
        'mobile':studentdata[0].mobile,
        'fee':studentdata[0].fee,
        'notice':notice
    }
    return render(request,'school/student_dashboard_new.html',context=mydict)



@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_attendance_view(request):
    form=forms.AskDateForm()
    if request.method=='POST':
        form=forms.AskDateForm(request.POST)
        if form.is_valid():
            date=form.cleaned_data['date']
            studentdata=models.StudentExtra.objects.all().filter(user_id=request.user.id,status=True)
            attendancedata=models.Attendance.objects.all().filter(date=date,cl=studentdata[0].cl,roll=studentdata[0].roll)
            mylist=zip(attendancedata,studentdata)
            return render(request,'school/student_view_attendance_page.html',{'mylist':mylist,'date':date})
        else:
            print('form invalid')
    return render(request,'school/student_view_attendance_ask_date.html',{'form':form})









# for aboutus and contact us
def aboutus_view(request):
    return render(request,'school/aboutus.html')

def contactus_view(request):
    sub = forms.ContactusForm()
    if request.method == 'POST':
        sub = forms.ContactusForm(request.POST)
        if sub.is_valid():
            email = sub.cleaned_data['Email']
            name=sub.cleaned_data['Name']
            message = sub.cleaned_data['Message']
            send_mail(str(name)+' || '+str(email),message,settings.EMAIL_HOST_USER, settings.EMAIL_RECEIVING_USER, fail_silently = False)
            return render(request, 'school/contactussuccess.html')
    return render(request, 'school/contactus.html', {'form':sub})

def takeexam(request):
    return render(request,'school/QuizHome.html')

def quizindex(request):
    return render(request,'school/quizindex.html')
def admin_add_course(request):
    courses=models.courses.objects.all()
    return render(request,'school/admin_add_course.html',{'courses':courses})
def add_course(request):
    return render(request,'school/add_course.html')
def insert_course(request):
    coursename=request.POST.get("coursename")
    coursecode=request.POST.get("coursecode")
    credits=request.POST.get("credits")
    handout=request.POST.get("handout")
    ref=models.courses(coursename=coursename,coursecode=coursecode,credits=credits,handoutfilename=handout)
    ref.save()
    return redirect('admin_add_course')

def studentcoursesinit(stid,courses):
    for i in courses:
        tmp=models.student_registered_courses(student_id=stid,courseid=i.id)
        tmp.save()

def student_courses(request):
    courses = models.courses.objects.all()
    userid = models.StudentExtra.objects.all().filter(user_id=request.user.id)
    if(len(models.student_registered_courses.objects.all().filter(student_id=userid[0].roll))==0):
        studentcoursesinit(userid[0].roll,courses)
    students_registered=models.student_registered_courses.objects.all().filter(student_id=userid[0].roll)
    # print(students_registered[0].status)
    mylist=zip(courses,students_registered)
    return render(request, 'school/student_courses.html', {'mylist':mylist})
def student_register_course(request,cid):
    userid = models.StudentExtra.objects.all().filter(user_id=request.user.id)
    if(models.student_registered_courses.objects.filter(student_id=userid[0].roll,courseid=cid)[0].status=="Registered"):
        return render(request,"school/registererror.html")
    else:
        models.student_registered_courses.objects.filter(student_id=userid[0].roll,courseid=cid).update(status="Registered")
        return redirect('student_courses')

def Timetable(request):
    return render(request,'school/TimeTable.html')

def teacher_courses(request):
    courses = models.teacher_registered_courses.objects.all().filter(teacher_id=request.user.id)
    return render(request,'school/teacher_courses.html',{'courses': courses})
def teacher_add_course(request):
    courses = models.courses.objects.all()
    teacher_courses=models.teacher_registered_courses.objects.all().filter(teacher_id=request.user.id)
    temp=[]
    for i in teacher_courses:
        temp.append(i.coursename)
    lst=[]
    for i in courses:
        if(i.coursename not in temp):
            lst.append(i.coursename)
    return render(request, 'school/teacher_add_course.html', {'courses': lst})
def insert_course_teacher(request):
    cname=request.POST.get("course")
    course=models.courses.objects.all().filter(coursename=cname)
    add=models.teacher_registered_courses(coursename=course[0].coursename,coursecode=course[0].coursecode,credits=course[0].credits,handoutfilename=course[0].handoutfilename,teacher_id=request.user.id,course_id=course[0].id)
    add.save()
    return redirect('teacher_courses')
def teacher_delete_course(request,id):
    course=models.teacher_registered_courses.objects.all().filter(id=id)
    course.delete()
    return redirect('teacher_courses')
def upload(request):
    if request.method == 'POST':
        form = forms.MyfileUploadForm(request.POST,request.FILES)
        if form.is_valid():
            book_id = form.cleaned_data['book_id']
            book_name = form.cleaned_data['book_name']
            book_author = form.cleaned_data['book_author']
            book_desc = form.cleaned_data['book_desc']
            book_pub_date = form.cleaned_data['book_pub_date']
            book_pic = form.cleaned_data['book_pic']
            book_file = form.cleaned_data['book_file']
            book_tag1 = form.cleaned_data['book_tag1']
            book_tag2 = form.cleaned_data['book_tag2']
            book_tag3 = form.cleaned_data['book_tag3']
            book_tag4 = form.cleaned_data['book_tag4']

            models.library(book_id = book_id,
                        book_name = book_name,
                        book_author = book_author,
                        book_desc = book_desc,
                        book_pub_date = book_pub_date,
                        book_pic = book_pic,
                        book_file = book_file,
                        book_tag1 = book_tag1,
                        book_tag2 = book_tag2,
                        book_tag3 = book_tag3,
                        book_tag4 = book_tag4).save()
            return HttpResponse("Book Uploaded Successfully.")
        else:
            return HttpResponse('Failed to Upload Book!')
    else:
        context={
            'form': forms.MyfileUploadForm()
        }
        return render(request, "school/upload_book.html",context)
def view_books(request):
    all_data = models.library.objects.all()
    context = {
        'data':all_data
    }
    return render(request,'school/view_books.html', context)
def upload_book(request):
    return render(request,'school/upload_book.html')

def insert_quiz_result(request):
    result=request.POST.get("quiz_result")
    userid = models.StudentExtra.objects.all().filter(user_id=request.user.id)
    quiz=models.quiz_result.objects.all().filter(student_id=userid[0].roll)
    if(len(quiz)!=0):
        models.quiz_result.objects.all().filter(student_id=userid[0].roll).update(attempted_time=datetime.now())
        models.quiz_result.objects.all().filter(student_id=userid[0].roll).update(score=result)
        models.quiz_result.objects.all().filter(student_id=userid[0].roll).update(attempted_date=date.today())
    else:
        tmp=models.quiz_result(student_id=userid[0].roll,score=result)
        tmp.save()
    return redirect('student-dashboard')
def average_quiz_analytics(request):
    quiz=models.quiz_result.objects.all()
    scores=[int(i.score) for i in quiz]
    res=sum(scores)//len(scores)
    score_average_graph=quiz_analytics_bar(['Average Student Score in the Quiz'],[res],'Overall performance of Students','Student Marks','')
    return render(request,'school/quiz_analytics.html',{'score_average_graph':score_average_graph})
def quiz_analytics_filter(request):
    minval=request.POST.get('minval')
    labels=[i for i in range(0,int(minval)+1)]
    quiz = models.quiz_result.objects.all()
    scores = [int(i.score) for i in quiz]
    values=[]
    for i in labels:
        c=0
        for j in scores:
            if(i==j):
                c+=1
        values.append(c)
    filtered_graph = quiz_analytics_filter_bar(labels, values,
                                             'Analytics of Students with minimum marks of '+minval,'marks','Number of Students')
    return render(request, 'school/quiz_analytics_filtered.html', {'filtered_graph': filtered_graph})
def parent(request):
    parents=models.parent.objects.all()
    return render(request,'school/parent.html',{'parent':parents})
def view_children(request,ph):
    students=models.StudentExtra.objects.all()
    parent=models.parent.objects.all().filter(phone=ph)
    lst=[]
    for i in parent:
        for j in students:
            if(i.student_id==j.roll):
                lst.append(j)
    return render(request,'school/view_children.html',{'children':lst})
def insert_parent(request):
    name=request.POST.get('name')
    student_id=request.POST.get('student_id')
    phone=request.POST.get('phone')
    password=request.POST.get('password')
    tmp = models.parent(name=name, student_id=student_id, phone=phone, password=password)
    tmp.save()
    return redirect('parent')
def add_parent(request):
    return render(request,'school/add_parent.html')
def parent_login(request):
    return render(request,'school/parentlogin.html')
def validate_parent(request):
    phone=request.POST.get('phone')
    password=request.POST.get('password')
    parent=models.parent.objects.all()
    for i in parent:
        if(i.phone==phone and i.password==password):
            return render(request,'school/parent_dashboard.html',{'parent':i})
    return redirect('parent_login')
def parent_view_attendance(request,phone):
    students = models.StudentExtra.objects.all()
    parent = models.parent.objects.all().filter(phone=phone)
    lst = []
    for i in parent:
        for j in students:
            if (i.student_id == j.roll):
                lst.append(j)
    return render(request, 'school/parent_view_attendance.html', {'student': lst})
def parent_view_attendance_filtered(request,roll):
    attendance=models.Attendance.objects.all().filter(roll=roll)
    return render(request,'school/parent_view_attendance_filtered.html',{'attendance':attendance})
def parent_view_quizresult(request,phone):
    students = models.StudentExtra.objects.all()
    parent = models.parent.objects.all().filter(phone=phone)
    lst = []
    for i in parent:
        for j in students:
            if (i.student_id == j.roll):
                lst.append(j)
    return render(request, 'school/parent_view_quizresult.html', {'student': lst})
def parent_view_quizresult_filtered(request,roll):
    quizresult=models.quiz_result.objects.all().filter(student_id=roll)
    return render(request,'school/parent_view_quizresult_filtered.html',{'quizresult':quizresult})
def smsalert(request):
    return render(request,'school/smsalert.html')
def sendsms(request):
    studentid=request.POST.get('studentid')
    parent=models.parent.objects.all().filter(student_id=studentid)
    return render(request,'school/sendsms.html',{'parent':parent[0]})
def insert_sms(request):
    message=request.POST.get('message')
    phonenumber=request.POST.get('phonenumber')
    sendsms=models.sendsms(message=message,phonenumber=phonenumber)
    sendsms.save()
    return redirect('teacher-dashboard')



