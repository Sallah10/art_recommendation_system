from django.contrib import admin
from .models import Art_Work, UserInteraction
from django.contrib.auth.models import Group, User
# Register your models here.

# Register your models here.
admin.site.register(Art_Work)
admin.site.register(UserInteraction)


class UserAdmin(admin.ModelAdmin):
	model=User
	fields=('first_name', 'last_name', 'username', 'email',)
	list_display=('username', 'email',) 
	


admin.site.unregister(User)
admin.site.register(User, UserAdmin)