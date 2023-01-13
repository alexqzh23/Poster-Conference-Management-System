import json

from numpy import *
from django.db import models
from cms.models_conference import Programme


# Create your models here.


class Poster(models.Model):
    """
    record the information of one poster
    """
    posterID = models.AutoField(primary_key=True)
    title = models.TextField()
    abstract = models.TextField()
    authorName = models.CharField(max_length=128)
    authorEmail = models.CharField(unique=True, max_length=128)
    supervisorName = models.CharField(max_length=128)
    poster_file = models.ImageField(upload_to='posters')  # storage path of poster picture
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE)

    def get_posterID(self):
        return self.posterID

    def get_abstract(self):
        return self.abstract

    def get_authorName(self):
        return self.authorName

    def get_authorEmail(self):
        return self.authorEmail

    def get_supervisorName(self):
        return self.supervisorName

    def get_programmeName(self):
        return self.programmeName

    # set method for all the attributes
    def edit_abstract(self, abstract):
        self.abstract = abstract

    def edit_authorName(self, authorName):
        self.authorName = authorName

    def edit_authorEmail(self, authorEmail):
        self.authorEmail = authorEmail

    def edit_supervisorName(self, supervisorName):
        self.supervisorName = supervisorName

    def edit_programmeName(self, programmeName):
        self.programmeName = programmeName

    def __str__(self):
        return "Poster：" + str(self.get_posterID())

    class Meta:
        db_table = 'Poster'


class PopularPoster(models.Model):
    """
    record the poster with the highest votes
    """
    posterID = models.OneToOneField(Poster, on_delete=models.CASCADE, primary_key=True)
    programmeName = models.ForeignKey(Programme, on_delete=models.CASCADE)

    def __str__(self):
        return "Popular Poster：" + str(self.posterID)

    class Meta:
        db_table = 'PopularPoster'


class PosterPublicUse(models.Model):
    """
    record the posters with their votes
    """
    posterID = models.OneToOneField(Poster, on_delete=models.CASCADE, primary_key=True)
    votes = models.IntegerField(default=0)

    def get_votes(self):
        return self.votes

    def increase_vote_count(self):
        self.votes += 1

    def __str__(self):
        return "Poster Votes:" + str(self.votes)

    class Meta:
        db_table = 'PosterPublicUse'


class PosterInternalUse(models.Model):
    """
    record the posters with their judge scores
    """
    posterID = models.OneToOneField(Poster, on_delete=models.CASCADE, primary_key=True)
    judgeScores = models.JSONField(default=json.loads('{}'))  # score_record: {'judge_name':score}

    def cal_judgeAvg(self):
        return round(mean([float(self.judgeScores[item]) for item in self.judgeScores]), 2)

    def set_score(self, user_id, score):
        self.judgeScores.update({user_id: score})
        self.judgeScores[str(user_id)] = float(score)

    def get_score(self, user_id):
        try:  # try-catch-except in case of some posters doesn't have score
            score = self.judgeScores[user_id]
            return score
        except KeyError:
            return None

    def save(self, *args, **kwargs):
        super(PosterInternalUse, self).save(*args, **kwargs)  # confirm the score and save it
        print('Did this attribute update? (attr):', self.judgeScores)
        print('Save method executed!')

    def __str__(self):
        return "Poster Scores By Judges:" + str(self.judgeScores)

    class Meta:
        db_table = 'PosterInternalUse'


class ProgrammeWinnerPoster(models.Model):
    """
    record the poster with highest score in the programme
    """
    posterID = models.OneToOneField(Poster, on_delete=models.CASCADE, primary_key=True)
    scoresByHJ = models.JSONField(default=json.loads('{}'))  # score_record: {'judge_name':score}

    def cal_hjAvg(self):
        return round(mean([self.scoresByHJ[item] for item in self.scoresByHJ]), 2)

    #
    def set_hjscore(self, user_id, score):
        self.scoresByHJ.update({user_id: float(score)})

    def get_hjscore(self, user_id):
        try:  # try-catch-except in case of some posters doesn't have score
            score = self.scoresByHJ[user_id]
            return score
        except KeyError:
            return None

    def save(self, *args, **kwargs):
        super(ProgrammeWinnerPoster, self).save(*args, **kwargs)  # confirm the head judge score and save it
        print('Did this attribute update? (attr):', self.scoresByHJ)
        print('Save method executed!')

    def __str__(self):
        return "Programme Winner Poster" + str(self.scoresByHJ)

    class Meta:
        db_table = 'ProgrammeWinnerPoster'


class DivisionWinnerPoster(models.Model):
    """
    record the posters with highest score in the division
    """
    posterID = models.ForeignKey(Poster, related_name="poster", on_delete=models.CASCADE, primary_key=True)
    divisionName = models.CharField(max_length=128)

    def __str__(self):
        return "Division:" + str(self.divisionName)

    class Meta:
        db_table = 'DivisionWinnerPoster'
