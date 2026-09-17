from django.contrib import admin
from .models import Profile, Type_User
from django.contrib.auth.models import Group, User
# Register your models here.

# Register your models here.

admin.site.register(Type_User)

class ProfileInline(admin.StackedInline):
	model=Profile

class UserAdmin(admin.ModelAdmin):
	model=User
	fields=('first_name', 'last_name', 'username', 'email',)
	list_display=('username', 'email',) 
	inlines=[ProfileInline]


admin.site.unregister(User)
admin.site.register(User, UserAdmin)