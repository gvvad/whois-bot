from django.db import models
#import datetime
from django.utils import timezone


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

        #delta_a = datetime.datetime.now() + datetime.timedelta(days=30)
        delta_a = timezone.now() + timezone.timedelta(days=30)
        #delta_b = datetime.datetime.now() - datetime.timedelta(days=5)
        delta_b = timezone.now() + timezone.timedelta(days=5)

        result = dict()
        for item in WhoisTbotModel.objects.filter(exp_date__lte=delta_a, last_notif_date__lte=delta_b):
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