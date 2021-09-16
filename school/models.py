from datetime import datetime, date
from django.db import models
from django.contrib.auth.models import User
from twilio.rest import Client
# Create your models here.
from django.template.backends import django


class TeacherExtra(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    salary = models.PositiveIntegerField(null=False)
    joindate=models.DateField(auto_now_add=True)
    mobile = models.CharField(max_length=40)
    status=models.BooleanField(default=False)
    def __str__(self):
        return self.user.first_name
    @property
    def get_id(self):
        return self.user.id
    @property
    def get_name(self):
        return self.user.first_name+" "+self.user.last_name




classes=[('one','one'),('two','two'),('three','three'),
('four','four'),('five','five'),('six','six'),('seven','seven'),('eight','eight'),('nine','nine'),('ten','ten')]
class StudentExtra(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    roll = models.CharField(max_length=10)
    mobile = models.CharField(max_length=40,null=True)
    fee=models.PositiveIntegerField(null=True)
    cl= models.CharField(max_length=10,choices=classes,default='one')
    status=models.BooleanField(default=False)
    @property
    def get_name(self):
        return self.user.first_name+" "+self.user.last_name
    @property
    def get_id(self):
        return self.user.id
    def __str__(self):
        return self.user.first_name



class Attendance(models.Model):
    roll=models.CharField(max_length=10,null=True)
    date=models.DateField()
    cl=models.CharField(max_length=10)
    present_status = models.CharField(max_length=10)



class Notice(models.Model):
    date=models.DateField(auto_now=True)
    by=models.CharField(max_length=20,null=True,default='school')
    message=models.CharField(max_length=500)

class courses(models.Model):
    coursename=models.CharField(max_length=50)
    coursecode=models.CharField(max_length=20)
    credits=models.CharField(max_length=10)
    handoutfilename=models.CharField(max_length=50)
class student_registered_courses(models.Model):
    student_id=models.CharField(max_length=20)
    courseid=models.CharField(max_length=10)
    status=models.CharField(max_length=20,default="Click to Register")
class teacher_registered_courses(models.Model):
    coursename = models.CharField(max_length=50)
    coursecode = models.CharField(max_length=20)
    credits = models.CharField(max_length=10)
    handoutfilename = models.CharField(max_length=50)
    teacher_id=models.CharField(max_length=20)
    course_id=models.CharField(max_length=20)
class library(models.Model):
    id = models.AutoField(primary_key=True)
    book_id = models.CharField(max_length=100, default="NA")
    book_name = models.CharField(max_length=50, default="NA")
    book_author = models.CharField(max_length=50, default="NA")
    book_pub_date = models.CharField(max_length=20, default="NA")
    book_desc = models.TextField(max_length=255, default="NA")
    book_tag1 = models.CharField(max_length=20, default="NA")
    book_tag2 = models.CharField(max_length=20, default="NA")
    book_tag3 = models.CharField(max_length=20, default="NA")
    book_tag4 = models.CharField(max_length=20, default="NA")
    book_pic = models.ImageField(null=True, blank=True, default='book.jpg')
    book_file = models.FileField(upload_to='books/')
class quiz_result(models.Model):
    id = models.AutoField(primary_key=True)
    student_id=models.CharField(max_length=50,default='NA')
    attempted_time=models.TimeField(default=datetime.now())
    attempted_date=models.DateField(default=date.today())
    score=models.CharField(max_length=10)
class parent(models.Model):
    id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=50)
    student_id=models.CharField(max_length=15)
    phone=models.CharField(max_length=11)
    password=models.CharField(max_length=50)

class sendsms(models.Model):
    message=models.CharField(max_length=1000)
    phonenumber=models.CharField(max_length=20)
    def __str__(self):
        return str(self.message)
    def __str__(self):
        return str(self.phonenumber)
    def save(self,*args,**kwargs):
        account_sid="ACfbb2c834381097fb0212d1c95b0f578d"
        auth_token="1a7cbe997d7e4e38152e16ecdf21a871"
        client=Client(account_sid,auth_token)

        message=client.messages.create(
            body=f'{self.message}',
            from_='+12565810736',
            to='+91'+self.phonenumber
        )
        print(message.sid)
        return super().save(*args,**kwargs)