import json, os
from random import shuffle

from django.contrib.auth.backends import ModelBackend

from cms import models_poster, models_conference, system_function
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.db.models import Q
from cms.models_conference import Conference
import cms.system_function
from cms.forms import updatePosterForm
from cms.models import Attendee
from cms.models_conference import Programme
from cms.models_luckdraw import LuckyDrawer
from cms.models_poster import PosterPublicUse, PosterInternalUse, Poster, ProgrammeWinnerPoster, DivisionWinnerPoster
from cms.models_committee import ProgrammeJudge, HeadJudge
import cms.system_function

User = get_user_model()


# Create your views here.

class CustomBackend(ModelBackend):

    def authenticate(self, username=None, user_id=None, password=None, email=None, **kwargs):
        try:
            if email is not None:
                user = Attendee.objects.get(email=email)
                user = User.objects.get(user_id=user.user_id)
                return user
            else:
                user = User.objects.exclude(user_type='attendee').filter(user_id=user_id).select_related().get()
                # user = User.objects.get(user_id=user_id)
                subclass = str(user.user_type).replace(' ', '').lower()
                print(user.user_type, eval('user.' + subclass + '.get_pwd()'))
                if eval('user.' + subclass + '.get_pwd()') == password:
                    return user
            # return user
        except Exception as e:
            print(e)
            return None
    #
    # def get_user(self, user_id):
    #     try:
    #         return User.objects.get(user_id=user_id)
    #
    #     except User.DoesNotExist:
    #         return None


def context_data():
    """
    :return: basic content for webpages
    """
    context = {
        'site_name': 'UIC DST Conference',
        'page': 'home',
        'page_title': 'Home',
        'programmes': models_conference.Programme.objects.all()
    }
    return context


def get_related_info(user, poster):
    """
    get related information with user and poster
    :param user: user object
    :param poster: poster object
    :return: bundled related info
    """
    info = {'is_pgm_winner': False}
    try:
        # check if current poster is Division Winner Poster
        dw = DivisionWinnerPoster.objects.get(posterID=poster.posterID)
        info['is_div_winner'] = True
        info['division'] = dw.divisionName
    except DivisionWinnerPoster.DoesNotExist:
        # if not, check is it Programme Winner Poster
        try:
            ProgrammeWinnerPoster.objects.get(posterID=poster.posterID)
            info['is_pgm_winner'] = True
        except ProgrammeWinnerPoster.DoesNotExist:
            pass

    pi = Poster.objects.select_related().filter(posterID=poster.posterID).get()

    if user.is_anonymous:
        return info
    if user.user_type == 'Attendee':
        """
        votes: vote the poster got
        isVote: if the attendee is voted or not
        """
        info['votes'] = pi.posterpublicuse.get_votes()
        info['isVote'] = user.attendee.get_vote_status()
    elif user.user_type == 'Programme Judge':
        """
        auth: if the poster and the judge are belong to the same programme
        score: the score that judge gave to the poster
        j_all_finished: if all judges finished score posters in their (the same as the judge's)r programme
        pAvg: the average programme score that the poster received
        unfinished: the poster that the judge has not scored
        """
        info['auth'] = False
        info['score'] = None
        if pi.programme == user.programmejudge.program_name:
            info['auth'] = True
            score = pi.posterinternaluse.get_score(user.user_id)
            if score is not None:
                info['score'] = score
                scored = len(pi.posterinternaluse.judgeScores.keys())
                total = ProgrammeJudge.objects.filter(program_name=pi.programme).count()
                print(scored, " ", total)
                if scored < total:
                    info['j_all_finished'] = False
                else:
                    info['pAvg'] = PosterInternalUse.objects.get(posterID=poster.posterID).cal_judgeAvg()
                    info['j_all_finished'] = True

            self_unfinished = list()
            all_num = Poster.objects.filter(programme=user.programmejudge.program_name)
            for p in all_num:
                if not p.posterinternaluse.get_score(user.user_id) and p.posterID != poster.posterID:
                    self_unfinished.append(p)
            info['unfinished'] = self_unfinished
    elif user.user_type == 'Head Judge':
        """
        auth: if the poster and the judge are belong to the same programme
        score: the score that judge gave to the poster
        pgm_all_finished: if all programme judges finished score posters
        pAvg: the average programme score that the poster received
        unfinished: the poster that the judge has not scored
        j_all_finished: if all Header judge have finished scoring
        """
        info['pAvg'] = PosterInternalUse.objects.get(posterID=poster.posterID).cal_judgeAvg()
        info['score'] = None
        info['pgm_all_finished'] = False
        info['pgm_finished'] = False
        try:
            ppw = ProgrammeWinnerPoster.objects.get(posterID=poster.posterID)
            info['pgm_finished'] = True
            score = ppw.get_hjscore(user.user_id)
            if score is not None:
                info['score'] = ppw.get_hjscore(user.user_id)
                scored = len(ppw.scoresByHJ.keys())
                total = HeadJudge.objects.all().count()
                print(scored, " ", total)
                # check if all judge in the same programme as passed judge have scored all posters
                if scored == total:
                    info['j_all_finished'] = True

            # check if passed judge finished all posters
            all_num = ProgrammeWinnerPoster.objects.all()
            if all_num.count() == Programme.objects.all().count():
                info['pgm_all_finished'] = True
                self_unfinished = list()
                for p in all_num:
                    if not p.get_hjscore(user.user_id) and p.posterID_id != poster.posterID:
                        self_unfinished.append(Poster.objects.get(posterID=p.posterID_id))
                info['unfinished'] = self_unfinished
        except Exception as e:
            print(e.__str__())
            try:

                ProgrammeWinnerPoster.objects.select_related().get(posterID__programme=poster.programme)
                info['pgm_finished'] = True
            except ProgrammeWinnerPoster.DoesNotExist:
                print('pgm_finished', e, )
    print(info)
    return info


def home(request):
    """
    render the home page with random poster order
    :param request:
    :return: home page
    """
    context = context_data()
    posters = list(Poster.objects.all())
    print(posters)
    shuffle(posters)
    context['page'] = 'home'
    context['page_title'] = 'Home'
    context['latest_top'] = posters[:4]
    context['latest_bottom'] = posters[4:]
    print(posters)
    return render(request, 'home.html', context)


def home_pop(request):
    """
    render the home page with popularity poster order
    :param request:
    :return:
    """
    context = context_data()
    posters = list()
    plist = PosterPublicUse.objects.all().order_by("votes")
    for poster in plist:
        posters.append(Poster.objects.get(posterID=poster.posterID_id))
    print(posters)
    context['page'] = 'home'
    context['page_title'] = 'Home'
    context['latest_top'] = posters[:4]
    context['latest_bottom'] = posters[4:]
    print(posters)
    return render(request, 'home_pop.html', context)


def login_page(request):
    """
    render the login page
    :param request:
    :return:  login page
    """
    context = context_data()
    return render(request, 'login.html', context)


# login
def login_user(request):
    """
    username & password login method
    :param request:
    :return: login status
    """
    resp = {"status": 'failed', 'msg': ''}
    if request.POST:
        user_id = request.POST['user_id']
        password = request.POST['password']
        if str(user_id).find('@') != -1:
            user = authenticate(email=user_id, password=password)
        else:  # check user's input information
            user = authenticate(user_id=user_id, password=password)
        print(user)
        if user is not None:
            login(request, user, 'cms.views.CustomBackend')
            resp['status'] = 'success'
        else:
            resp['msg'] = "Incorrect username or password"
    return HttpResponse(json.dumps(resp), content_type='application/json')


def logout_user(request):
    """
    logout user
    :param request:
    :return: redirect to home page
    """
    logout(request)
    return redirect('/')


def login_page_mail(request):
    """view for turning to link login page"""
    context = context_data()
    return render(request, 'login_mail.html', context)


def login_mail(request):
    """view for getting the email from front-end"""
    resp = {"status": 'failed', 'msg': ''}  # respond
    if request.POST:
        mail = request.POST['mail']
        # if email address is in correct format (which is uic email address)
        if str(mail).find('@mail.uic.edu.cn') != -1:
            user = authenticate(email=mail)
        else:
            user = None
            resp['msg'] = "Incorrect email format, please use your UIC email"
            return HttpResponse(json.dumps(resp), content_type='application/json')
        # if user exists, ask for enter webpage by using the received link
        # for avoiding user register more than once
        if user is not None:
            resp['msg'] = "You have already registered, please enter homepage through the link you received before."
            return HttpResponse(json.dumps(resp), content_type='application/json')
        # else send activate email and prompt user to check
        else:
            print('no')
            resp['msg'] = "Please check your email to activate your account."
            cms.system_function.send_mail(mail)
            login_page_mail(request)  # back to login page again
    return HttpResponse(json.dumps(resp), content_type='application/json')


def setup_page(request):
    """the page that shows conference detail info"""
    context = context_data()
    records = Conference.objects.get(conf_id=0)
    if records:
        content = cms.models_conference.Conference.get_content(records)
        rule = cms.models_conference.Conference.get_rule(records)
        date = cms.models_conference.Conference.get_date_time(records)
        context = {'content': content, 'rule': rule, 'date': date}
    else:
        Conference.objects.create(conf_id=0)
    return render(request, 'setup.html', context)


def setup_bpage(request):
    """view for turning to conference info page (setup page)"""
    return render(request, 'setup_conf.html')


def setup(request):
    """view for editing conference info"""
    context = context_data()
    if request.method == 'POST':
        content = request.POST.get('content', '')  # get new content
        rule = request.POST.get('rule', '')  # get new rule
        conf = Conference.objects.get(conf_id=0)
        Conference.objects.filter(conf_id=0).update(content=content, rule=rule)
        date = cms.models_conference.Conference.get_date_time(conf)
        context = {'content': content, 'rule': rule, 'date': date}
    return render(request, 'setup.html', context)


def view_poster(request, pk=None):
    """
    render single poster page
    :param request:
    :param pk: poster id
    :return: sigle poster page
    """
    context = context_data()
    poster = models_poster.Poster.objects.get(posterID=pk)
    context['page'] = 'post'
    context['page_title'] = poster.title
    context['poster'] = poster
    context['final_score'] = None
    context['final_pgm_score'] = None
    context['related_info'] = get_related_info(request.user, poster)
    try:
        # if Division Winner Poster is finalized
        DivisionWinnerPoster.objects.get()
        try:
            # if this poster is Programme Winner Poster
            pw = ProgrammeWinnerPoster.objects.get(posterID_id=pk)
            # this poster is not Division Winner Poster
            context['final_score'] = pw.cal_hjAvg()
        except ProgrammeWinnerPoster.DoesNotExist:
            # this poster is not Programme Winner Poster
            pi = PosterInternalUse.objects.get(posterID=pk)
            context['final_pgm_score'] = pi.cal_judgeAvg()
    except DivisionWinnerPoster.DoesNotExist:
        pass
    context['actions'] = False
    return render(request, 'single_post.html', context)


def upload_poster(request):
    """
    used for uploading the poster with its information to the database
    """
    if request.method == 'POST':
        form = updatePosterForm(request.POST)
        if not form.is_valid():  # form validation
            for ll in form:
                if ll.errors:
                    return JsonResponse({'code': 11, 'msg': ll.errors[0]})
        data = form.clean()
        if models_poster.Poster.objects.filter(authorEmail=data['authorEmail']).exists():
            return JsonResponse({"code": 1, 'msg': 'authorEmail exists'})
        if not models_conference.Programme.objects.filter(programme_name=data['programme_name']).exists():
            return JsonResponse({"code": 1, 'msg': 'Programme does not exists'})
        file = request.FILES.get('file')  # poster pictures
        if not file:
            return ({"code": 1, 'msg': 'File is None'})
        if not os.path.splitext(file.name)[1].lower() in ['.jpg', '.jpeg', '.bmp', '.gif', '.png', '.psd']:
            return JsonResponse({'code': 1, 'msg': 'The file format is incorrect'})  # file format check
        programme = models_conference.Programme.objects.filter(programme_name=data['programme_name']).first()
        models_poster.Poster.objects.create(title=data['title'], abstract=data['abstract'],
                                            authorName=data['authorName'], authorEmail=data['authorEmail'],
                                            supervisorName=data['supervisorName'], programme=programme,
                                            poster_file=file)
        return JsonResponse({"code": 0, "msg": "upload successfully"})
    programmes = models_conference.Programme.objects.all()
    return render(request, 'upload_poster.html', {'programmes': programmes})


def update_poster(request):
    """
    used for showing all the posters for following update step
    """
    posters = models_poster.Poster.objects.all()
    return render(request, 'update_poster.html', {'posters': posters})


def update_poster_detail(request, id):
    """
    used for obtaining the update date from front end after clicking the "update poster" button,
    edit the information of posters
    """
    if request.method == 'POST':
        form = updatePosterForm(request.POST)
        if not form.is_valid():  # form validation
            for ll in form:
                if ll.errors:
                    return JsonResponse({'code': 11, 'msg': ll.errors[0]})
        data = form.clean()
        if not models_poster.Poster.objects.filter(posterID=id).exists():
            return JsonResponse({"code": 1, 'msg': 'poster exists'})
        if models_poster.Poster.objects.exclude(posterID=id).filter(authorEmail=data['authorEmail']).exists():
            return JsonResponse({"code": 1, 'msg': 'authorEmail exists'})
        if not models_conference.Programme.objects.filter(programme_name=data['programme_name']).exists():
            return JsonResponse({"code": 1, 'msg': 'Programme exists'})
        file = request.FILES.get('file')
        if file and not os.path.splitext(file.name)[1].lower() in ['.jpg', '.jpeg', '.bmp', '.gif', '.png', '.psd']:
            return JsonResponse({'code': 1, 'msg': 'The file format is incorrect'})  # file format check
        programme = models_conference.Programme.objects.filter(programme_name=data['programme_name']).first()

        poster = models_poster.Poster.objects.filter(posterID=id).first()
        poster.programme = programme
        poster.title = data['title']
        poster.abstract = data['abstract']
        poster.authorName = data['authorName']
        poster.authorEmail = data['authorEmail']
        poster.supervisorName = data['supervisorName']
        if file:
            poster.poster_file = file
        poster.save()
        return JsonResponse({"code": 0, "msg": "edit successfully"})
    poster = models_poster.Poster.objects.filter(posterID=id).first()
    programmes = models_conference.Programme.objects.all()
    return render(request, 'update_poster_detail.html', {'poster': poster, 'programmes': programmes})


@login_required
def list_posters(request):
    """
    render evaluation page for judges
    :param request:
    :return: evaluation page
    """
    context = context_data()
    context['page'] = 'list_posters'
    context['page_title'] = 'Poster Evaluation'
    print(context)
    user = request.user
    if user.user_type == "Programme Judge":
        """
        poster_undone: posters that are underscored
        poster_done: posters that are scored
        poster_score: scores of posters
        poster_Avg: average scores of posters
        """
        poster_undone = list()
        poster_done = list()
        poster_score = {}
        poster_Avg = {}
        posters = Poster.objects.filter(programme=user.programmejudge.program_name)
        for poster in posters:
            if poster.posterinternaluse.get_score(user.user_id):
                poster_done.append(poster)
                poster_score[poster.posterID] = poster.posterinternaluse.get_score(user.user_id)
                scored = len(poster.posterinternaluse.judgeScores.keys())
                total = ProgrammeJudge.objects.filter(program_name=poster.programme).count()
                print(scored, " ", total)
                if scored == total:
                    poster_Avg[poster.posterID] = poster.posterinternaluse.cal_judgeAvg()
            else:
                poster_undone.append(poster)

        context['poster_done'] = poster_done
        context['poster_undone'] = poster_undone
        context['poster_score'] = poster_score
        context['poster_Avg'] = poster_Avg
        print(context)
    else:
        """
        Head judge
        poster_undone: posters that are underscored
        poster_done: posters that are scored
        poster_score: scores of posters
        poster_Avg: average scores of posters
        poster_final = final scores of posters
        """
        poster_undone = list()
        poster_done = list()
        poster_score = {}
        poster_final = {}
        poster_Avg = {}
        posters = ProgrammeWinnerPoster.objects.select_related().all()
        for poster in posters:
            poster_Avg[poster.posterID_id] = PosterInternalUse.objects.get(posterID=poster.posterID).cal_judgeAvg()
            if poster.get_hjscore(user.user_id):
                poster_done.append(Poster.objects.get(posterID=poster.posterID_id))
                poster_score[poster.posterID_id] = poster.get_hjscore(user.user_id)
                scored = len(poster.scoresByHJ.keys())
                total = HeadJudge.objects.count()
                if scored == total:
                    poster_final[poster.posterID_id] = poster.cal_hjAvg()
                print(scored, " ", total)
            else:
                poster_undone.append(Poster.objects.get(posterID=poster.posterID_id))

        context['poster_done'] = poster_done
        context['poster_undone'] = poster_undone
        context['poster_score'] = poster_score
        context['poster_Avg'] = poster_Avg
        try:
            DivisionWinnerPoster.objects.get()
            context['poster_final'] = poster_final
        except DivisionWinnerPoster.DoesNotExist:
            pass
        print(context)
    return render(request, 'posts.html', context)


def pgm_posters(request, pk=None):
    """
    return posters in given programme
    :param request:
    :param pk: programme name
    :return: programme posters
    """
    context = context_data()
    if pk is None:
        messages.error(request, "File not Found")
        return redirect('home-page')
    try:
        pgm = models_conference.Programme.objects.get(programme_name=pk)
    except:
        messages.error(request, "File not Found")
        return redirect('home-page')

    posters = list(Poster.objects.filter(programme=pk).all())
    print(posters)
    shuffle(posters)
    context['pgm'] = pgm
    context['page'] = 'pgm_posters'
    context['page_title'] = f'{pgm.abbr} Posters'
    context['latest_top'] = posters[:4]
    context['latest_bottom'] = posters[4:]

    return render(request, 'category.html', context)


def active_user(request, active_code):
    """view for activate the user who clicked the link"""
    email = cms.system_function.decryption(active_code)  # decode to get the email
    records = Attendee.objects.filter(email=email)  # search that whether the user have registered or not
    # if new user
    if not records:
        user_id = User.objects.create(user_type='Attendee')
        Attendee.objects.create(user_id_id=user_id, email=email)
    user = authenticate(email=email)
    login(request, user, 'cms.views.CustomBackend')
    # turn to home page with login status
    return redirect('home-page')


def vote_poster(request):
    """
    Attendee vote for posters
    :param request:
    :return:
    """
    resp = {"status": 'failed', 'msg': ''}
    print(request.body)
    try:
        data = json.loads(request.body)
        user_id = request.user.user_id
        poster_id = data['poster_id']
        user = Attendee.objects.get(user_id=user_id)
        user.set_vote_status()
        user.save()
        poster = PosterPublicUse.objects.get(posterID=poster_id)
        poster.increase_vote_count()
        poster.save()
        resp['status'] = 'success'
    except Attendee.DoesNotExist as e:
        print(e)
        resp['msg'] = 'Attendee not exist!'
    except PosterPublicUse.DoesNotExist as e:
        print(e)
        resp['msg'] = 'PosterPublicUse not exist!'
    return HttpResponse(json.dumps(resp), content_type='application/json')


def score_poster(request):
    """
    Judges score posters
    :param request:
    :return: score status
    """
    resp = {"status": 'failed', 'msg': ''}
    print(request.body)
    try:
        data = json.loads(request.body)
        user_id = request.user.user_id
        poster_id = data['poster_id']
        score = data['overall']
        user = User.objects.get(user_id=user_id)
        if user.user_type == "Programme Judge":
            poster = PosterInternalUse.objects.get(posterID=poster_id)
            poster.set_score(user_id, score)
            print(poster.judgeScores)
            poster.save()
            all_num = Poster.objects.filter(programme=user.programmejudge.program_name)
            unfinished = False
            # check if this judge finishes all posters
            for p in all_num:
                if not p.posterinternaluse.get_score(user.user_id):
                    unfinished = True
            print("Unfinished", unfinished)
            if not unfinished:
                # all finished
                user.programmejudge.set_score_status()
                user.programmejudge.save()
                try:
                    # check if all programme judge in programme is finished
                    ProgrammeJudge.objects.filter(program_name=user.programmejudge.program_name).get(score_status=0)
                except ProgrammeJudge.DoesNotExist:
                    # All finished finalized programme winner
                    finalize_pgm_winner(user.programmejudge.program_name)
        else:
            # head judge
            poster = ProgrammeWinnerPoster.objects.get(posterID=poster_id)
            poster.set_hjscore(user_id, score)
            poster.save()
            user.headjudge.score_status = True
            user.save()
            all_num = ProgrammeWinnerPoster.objects.all().count()
            unfinished = False
            # check if all programme is fished
            if all_num == Programme.objects.all().count():
                all = ProgrammeWinnerPoster.objects.all()
                # check if this header judge is fished
                for p in all:
                    if not p.get_hjscore(user.user_id):
                        unfinished = True
                print("Unfinished", unfinished)
                if not unfinished:
                    user.headjudge.set_score_status()
                    user.headjudge.save()
                    try:
                        # check if all head judge have finished
                        HeadJudge.objects.get(score_status=0)
                    except HeadJudge.DoesNotExist:
                        # all finished finalized division winner
                        finalize_div_winner()
        resp['status'] = 'success'
    except Exception as e:
        print(e)
        resp['msg'] = 'Exception!'
    # finally:
    return HttpResponse(json.dumps(resp), content_type='application/json')


def finalize_pgm_winner(program_name):
    """
    generate and store the programme winner
    :param program_name:
    :return: none
    """
    candidates = PosterInternalUse.objects.filter(posterID__programme=program_name).all()
    winner = None
    max_score = 0
    for poster in candidates:
        if poster.cal_judgeAvg() > max_score:
            winner = poster
    print(winner.posterID_id)
    ProgrammeWinnerPoster.objects.update_or_create(posterID=winner.posterID)


def finalize_div_winner():
    """
    generate and store division winner
    :return:
    """
    candidates = ProgrammeWinnerPoster.objects.all()
    winner = None
    max_score = 0
    for poster in candidates:
        if poster.cal_hjAvg() > max_score:
            winner = poster
    print(winner.posterID_id)
    DivisionWinnerPoster.objects.update_or_create(posterID=winner.posterID,
                                                  divisionName='Division of Science and Technology')

def lucky_draw(request):
    if request.method == 'GET':
        attendee = Attendee.objects.filter(vote_status=1).all()
        email_list = []
        for i in attendee:
            email_list.append(i.email)
        print(email_list)
        resp = {'email_list': email_list}
        return render(request, 'lucky_draw.html', {'objs': json.dumps(email_list)})
    else:
        first_prize_num = 3
        second_prize_num = 6
        third_prize_num = 9
        attendee = Attendee.objects.filter(vote_status=1).all()
        email_list = []
        for i in attendee:
            email_list.append(i.email)

        winner_list = []
        while first_prize_num != 0 or second_prize_num != 0 or third_prize_num != 0:
            if first_prize_num > 0:
                lucky_drawer = LuckyDrawer(1)
                winner_email = lucky_drawer.generate_first_winner(email_list)
                if winner_email is None:
                    break
                lucky_drawer.winner_id = winner_email
                lucky_drawer.prize_level = 1
                lucky_drawer.save()
                winner_list.append(winner_email)
                email_list.remove(winner_email)
                first_prize_num -= 1
            else:
                winner_list.append("")
            if second_prize_num > 0:
                lucky_drawer = LuckyDrawer(2)
                winner_email = lucky_drawer.generate_second_winner(email_list)
                if winner_email is None:
                    break
                lucky_drawer.winner_id = winner_email
                lucky_drawer.prize_level = 2
                lucky_drawer.save()
                winner_list.append(winner_email)
                email_list.remove(winner_email)
                second_prize_num -= 1
            else:
                winner_list.append("")
            if third_prize_num > 0:
                lucky_drawer = LuckyDrawer(3)
                winner_email = lucky_drawer.generate_third_winner(email_list)
                if winner_email is None:
                    break
                lucky_drawer.winner_id = winner_email
                lucky_drawer.prize_level = 3
                lucky_drawer.save()
                winner_list.append(winner_email)
                email_list.remove(winner_email)
                third_prize_num -= 1
            else:
                winner_list.append("")

        return render(request, 'winner_list.html', {'wn_list': winner_list})


def search(request):
    """
    used for searching posters with keywords without registration,possible keywords are title,
    author name and supervisor name
    """
    q = request.GET.get('q')
    error_msg = ''

    if not q:
        error_msg = 'Please enter keywords'
        messages.add_message(request, messages.ERROR, error_msg, extra_tags='danger')
        return render(request, 'home.html', {'error_msg': error_msg})

    poster_list = Poster.objects.filter(Q(title__icontains=q) | Q(authorName__icontains=q) |
                                        Q(supervisorName__icontains=q))
    print(poster_list)
    return render(request, 'home.html', {'error_msg': error_msg,
                                         'latest_top': poster_list})

