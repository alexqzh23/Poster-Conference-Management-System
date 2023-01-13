"""project URL Configuration

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

from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from cms import views

context = views.context_data()

urlpatterns = [
                  path('', views.home, name="home-page"),
                  path('popluar', views.home_pop, name="home-pop"),
                  path('login', views.login_page, name='login-page'),
                  path('logout', views.logout_user, name='logout'),
                  path('userlogin', views.login_user, name="login-user"),
                  path('setup', views.setup_page, name="setup-page"),
                  path('edit', views.setup_bpage, name="setup-edit"),
                  path('edit/conference', views.setup, name="setup-change"),
                  path('search/', views.search, name="search"),
                  path('post/<pk>', views.view_poster, name="view-poster"),
                  path('vote_poster', views.vote_poster, name="vote-poster"),
                  path('score_poster', views.score_poster, name="score-poster"),
                  path('vote_poster', views.vote_poster, name="vote-poster"),
                  path('upload_poster/', views.upload_poster, name="upload_poster"),
                  path('update_poster/', views.update_poster, name="update_poster"),
                  path('update_poster_detail/<int:id>', views.update_poster_detail, name="update_poster_detail"),
                  path('posts/', views.list_posters, name="list-posts"),
                  path('pgm_posters/<pk>', views.pgm_posters, name="pgm-posters"),
                  path('lucky_draw', views.lucky_draw, name="lucky-draw"),
                  path('login/mail', views.login_page_mail, name="login-page-mail"),
                  path('mailpage', views.login_mail, name="login-mail")
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
