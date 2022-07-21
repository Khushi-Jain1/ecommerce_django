from django.http import HttpResponse
from django.shortcuts import redirect

def unauthenticated_admin(view_func):
    def wrapper_func(self,request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_superuser == True:
                return redirect('admin:dashboard')
            else:
                return redirect('admin:unauthorized')
        else:
            return view_func(self,request, *args, **kwargs)
    return wrapper_func
