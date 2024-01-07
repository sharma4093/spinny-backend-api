
"""spinny URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from .views import BoxList, UpdateBox, MyBoxList, AddBox, DeleteBox
from .views import home
urlpatterns = [
    path('',home,name='home'),
    path('add-box/',AddBox.as_view(),name='add-box'),
    path('list-all-boxes/', BoxList.as_view(), name='box-list'),
    path('update-box/<int:pk>/', UpdateBox.as_view(), name='box-detail'),
    path('list-my-boxes/', MyBoxList.as_view(), name='my-box-list'),
    path('delete-box/<int:pk>/',DeleteBox.as_view(),name='delete-box'),
]