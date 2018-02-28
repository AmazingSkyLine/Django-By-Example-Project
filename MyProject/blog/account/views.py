from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from .forms import UserCreatForm, UserEditForm, ProfileEditFormn
from .models import Profile


def register(request):
    if request.method == 'POST':
        form = UserCreatForm(request.POST)
        if form.is_valid():
            # save()返回一个模型对象
            cd = form.cleaned_data
            print(cd)
            new_user = form.save(commit=False)
            new_user.set_password(cd['password'])
            new_user.save()
            Profile.objects.create(user=new_user,
                                   cute_name=cd['cute_name'])
            login(request, new_user)
            return render(request, 'account/register_done.html',
                          {'new_user': new_user})
    else:
        form = UserCreatForm()
    return render(request, 'account/register.html',
                  {'form': form})


@login_required
def profile_edit(request):
    if request.method == 'POST':
        print(request.POST.get('image'))
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditFormn(instance=request.user.profile, data=request.POST, files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('/account/profile/{}/'.format(request.user.id))
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditFormn(instance=request.user.profile)
    return render(request, 'account/profile_edit.html',
                  {'user_form': user_form,
                   'profile_form': profile_form,
                   'section': 'user'})


def user_profile(request, id):
    profile = get_object_or_404(Profile, user__id=id)
    return render(request, 'account/user_profile.html',
                  {'profile': profile,
                   'id': id,
                   'section': 'user'})
