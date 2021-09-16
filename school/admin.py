from django.contrib import admin
from .models import Attendance,StudentExtra,TeacherExtra,Notice,sendsms,parent
class StudentExtraAdmin(admin.ModelAdmin):
    pass
admin.site.register(StudentExtra, StudentExtraAdmin)

class TeacherExtraAdmin(admin.ModelAdmin):
    pass
admin.site.register(TeacherExtra, TeacherExtraAdmin)

class AttendanceAdmin(admin.ModelAdmin):
    pass
admin.site.register(Attendance, AttendanceAdmin)

class NoticeAdmin(admin.ModelAdmin):
    pass
admin.site.register(Notice, NoticeAdmin)
class sendsmsAdmin(admin.ModelAdmin):
    pass
admin.site.register(sendsms, sendsmsAdmin)
class parentAdmin(admin.ModelAdmin):
    pass
admin.site.register(parent, parentAdmin)
