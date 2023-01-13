from django.contrib.auth import get_user_model
from numpy import *
from django.db import models
from cms.models_conference import Programme

"""
Models related to committee subsystem
- CommitteeMember(models.Model) [Abstract]
- Judge(CommitteeMember) [Abstract]
- HeadJudge(Judge)
- ProgrammeJudge(Judge)
- Coordinator(CommitteeMember)
- Chairman(CommitteeMember)
"""
# Create your models here.
User = get_user_model()


class CommitteeMember(models.Model):
    """
    Abstract superclass for all committee member user type
    """
    user_id = models.OneToOneField(User, to_field='user_id', on_delete=models.CASCADE, primary_key=True)
    password = models.CharField(max_length=10)

    def get_pwd(self):
        return self.password

    def set_pwd(self, pwd):
        self.password = pwd

    def get_user_id(self):
        return self.user_id

    class Meta:
        abstract = True


class Judge(CommitteeMember):
    """
    Abstract superclass for all judges
    inherits from CommitteeMember class
    """
    # 0 indicates not scored yet
    score_status = models.BooleanField(default=0)

    def __str__(self):
        return "judge_id" + str(self.user_id)

    def get_score_status(self):
        return self.score_status

    def set_score_status(self):
        self.score_status = 1

    class Meta:
        abstract = True


class HeadJudge(Judge):
    """
       inherits from Judge class
       """

    def __str__(self):
        return "head_judge_id" + str(self.user_id)

    class Meta:
        db_table = 'HeadJudge'
        verbose_name = 'HeadJudges'
        verbose_name_plural = verbose_name


class ProgrammeJudge(Judge):
    """
    inherits from Judge class
    """
    program_name = models.ForeignKey(Programme, on_delete=models.DO_NOTHING)

    def get_pgm_name(self):
        return self.program_name

    def __str__(self):
        return "pgm_judge_id" + str(self.user_id)

    class Meta:
        db_table = 'ProgrammeJudge'
        verbose_name = 'ProgrammeJudges'
        verbose_name_plural = verbose_name


class Coordinator(CommitteeMember):
    """
    inherits from CommitteeMember class
    """
    program_name = models.ForeignKey(Programme, on_delete=models.DO_NOTHING)

    def get_pgm_name(self):
        return self.program_name

    def __str__(self):
        return "pgm_judge_id" + str(self.user_id)

    class Meta:
        db_table = 'Coordinator'
        verbose_name = 'Coordinators'
        verbose_name_plural = verbose_name


class Chairman(CommitteeMember):
    """
    inherits from CommitteeMember class
    """

    def __str__(self):
        return "chairman_id" + str(self.user_id)

    class Meta:
        db_table = 'Chairman'
        verbose_name = 'Chairmen'
        verbose_name_plural = verbose_name
