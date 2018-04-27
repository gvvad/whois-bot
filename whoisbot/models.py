from django.db import models
from django.db.models import Q, F, ExpressionWrapper
#import datetime
from django.utils import timezone

class TbotAwaitModel(models.Model):
    user_id = models.CharField(max_length=32)
    await = models.CharField(max_length=32)

    @staticmethod
    def get_await(user_id, clr=True):
        try:
            r = TbotAwaitModel.objects.filter(user_id=user_id)
            if r:
                res = r[0].await
                if clr:
                    r.delete()
                return res
        except:
            pass
        return None

    @staticmethod
    def set_await(user_id, mode):
        try:
            TbotAwaitModel(user_id=user_id, await=mode).save()
        except:
            pass

class WhoisTbotModel(models.Model):
    user_id = models.CharField(max_length=32)
    domain = models.CharField(max_length=256)
    last_notif_date = models.DateTimeField()
    exp_date = models.DateTimeField()


    @staticmethod
    def update_domain(user_id, domain, exp_date=None, last_notif_date=None):
        r = WhoisTbotModel.objects.filter(user_id=user_id, domain=domain)
        if r:
            if exp_date:
                r[0].exp_date = exp_date
            if last_notif_date:
                r[0].last_notif_date = last_notif_date
            r[0].save()
        else:
            WhoisTbotModel(user_id=user_id,
                           domain=domain,
                           exp_date=exp_date,
                           last_notif_date=timezone.now()
                           ).save()

    @staticmethod
    def list_notif():
        t_now = timezone.now()
        df_a = t_now + timezone.timedelta(days=90)
        db_a = t_now - timezone.timedelta(days=60)

        df_b = t_now + timezone.timedelta(days=30)
        db_b = t_now - timezone.timedelta(days=15)

        df_c = t_now + timezone.timedelta(days=15)
        db_c = t_now - timezone.timedelta(days=8)

        df_d = t_now + timezone.timedelta(days=7)
        db_d = t_now - timezone.timedelta(days=6)

        df_e = t_now + timezone.timedelta(days=1)
        db_e = t_now - timezone.timedelta(days=1)

        result = dict()
        for item in WhoisTbotModel.objects.\
            filter(Q(exp_date__lte=df_a, last_notif_date__lte=db_a) |
                   Q(exp_date__lte=df_b, last_notif_date__lte=db_b) |
                   Q(exp_date__lte=df_c, last_notif_date__lte=db_c) |
                   Q(exp_date__lte=df_d, last_notif_date__lte=db_d) |
                   Q(exp_date__lte=df_e, last_notif_date__lte=db_e)
                   ):
            result.setdefault(item.user_id, []).append({"domain": item.domain, "exp_date": item.exp_date})

        return result

    @staticmethod
    def domain_notif(user_id, domain):
        r = WhoisTbotModel.objects.filter(user_id=user_id, domain=domain)
        if r:
            r[0].last_notif_date = timezone.now()
            r[0].save()

    @staticmethod
    def remove_domain(user_id, domain):
        WhoisTbotModel.objects.filter(user_id=user_id, domain=domain).delete()

    @staticmethod
    def remove_user(user_id):
        WhoisTbotModel.objects.filter(user_id=user_id).delete()

    @staticmethod
    def list_domains(user_id):
        for item in WhoisTbotModel.objects.filter(user_id=user_id):
            yield {"domain": item.domain,
                   "exp_date": item.exp_date
                   }
