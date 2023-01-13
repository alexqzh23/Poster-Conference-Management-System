from django.contrib.auth import get_user_model
from django.utils import timezone
from numpy import *
from django.db import models

User = get_user_model()


class Rule(models.Model):
    """class of conference rule, with limitations of prizes and judges"""
    msg = 'Conference Rule'
    rule_id = models.AutoField(primary_key=True, verbose_name='conf_no')
    rule = models.CharField(max_length=1000, default=msg)
    num_of_judges = models.IntegerField(default=18)
    num_of_head_judge = models.IntegerField(default=2)
    num_of_fir_prize = models.IntegerField(default=3)
    num_of_sec_prize = models.IntegerField(default=5)
    num_of_thr_prize = models.IntegerField(default=10)

    def get_rule(self):
        return self.rule

    def get_judge_num(self):
        return self.num_of_judges

    def get_hjudge_num(self):
        return self.num_of_head_judge

    def get_fir_prize_num(self):
        return self.num_of_fir_prize

    def get_sec_prize_num(self):
        return self.num_of_sec_prize

    def get_thr_prize_num(self):
        return self.num_of_thr_prize

    def edit_rule(self, rule):
        Rule.objects.filter(rule_id=self.rule_id).update(rule=rule)
        self.rule = rule

    def edit_judge_num(self, num):
        Rule.objects.filter(rule_id=self.rule_id).update(num_of_judges=num)
        self.num_of_judges = num

    def edit_hjudge_num(self, num):
        Rule.objects.filter(rule_id=self.rule_id).update(num_of_head_judge=num)
        self.num_of_head_judge = num

    def edit_fir_prize_num(self, num):
        Rule.objects.filter(rule_id=self.rule_id).update(num_of_fir_prize=num)
        self.num_of_fir_prize = num

    def edit_sec_prize_num(self, num):
        Rule.objects.filter(rule_id=self.rule_id).update(num_of_sec_prize=num)
        self.num_of_sec_prize = num

    def edit_thr_prize_num(self, num):
        Rule.objects.filter(rule_id=self.rule_id).update(num_of_thr_prize=num)
        self.num_of_thr_prize = num

    class Meta:
        db_table = 'Rule'
        verbose_name = 'Rule'


class Conference(models.Model):
    """class of conference, with information about it"""
    msg_c = 'Conference Content ........'  # default message of content
    msg_r = 'Conference Rule ........'  # default message of rule
    conf_id = models.AutoField(primary_key=True, verbose_name='conf_no', default=0)
    date_time = models.DateTimeField(default=timezone.now)  # date_time is automatically equal to the object create time
    content = models.CharField(max_length=128, default=msg_c)
    rule = models.CharField(max_length=9000, default=msg_r)

    def get_rule(self):
        return self.rule

    def get_conf_id(self):
        return self.conf_id

    def get_date_time(self):
        return self.date_time

    def get_content(self):
        return self.content

    def edit_content(self, content):
        Conference.objects.filter(conf_id=self.conf_id).update(content=content)
        self.date = content

    def edit_rule(self, rule):
        Conference.objects.filter(conf_id=self.conf_id).update(rule=rule)
        self.rule = rule

    class Meta:
        db_table = 'Conference'
        verbose_name = 'Conference'


class Programme(models.Model):
    """programme is a class for other related class to reference programme name"""
    programme_name = models.CharField(primary_key=True, max_length=128)
    abbr = models.CharField(max_length=128, unique=True)  # abbreviation of programme name

    def get_pgm_name(self):
        return self.programme_name

    def get_abbr(self):
        return self.abbr

    def __str__(self):
        return "Programme:" + str(self.programme_name)

    class Meta:
        db_table = 'Programme'
        verbose_name = 'Programme'
