import socket
import logging
import datetime


class Whois(object):

    class Response(object):
        def __init__(self,
                     name="",
                     registrar="",
                     create_date=None,
                     update_date=None,
                     exp_date=None):
            self.name = name
            self.registrar = registrar
            self.create_date = create_date
            self.update_date = update_date
            self.exp_date = exp_date

    @staticmethod
    def query(domain):
        zone = domain.lower().split(".")[-1]
        try:
            if zone == "ua":
                return Whois._ua_request(domain)
            elif zone == "com" or zone == "net" or zone == "edu":
                return Whois._com_request(domain)
            elif zone == "org":
                return Whois._org_request(domain)
            elif zone == "ru":
                return Whois._ru_request(domain)
            else:
                return Whois.Response()
        except Exception:
            return Whois.Response()

    @staticmethod
    def _whois_request(whois_server, domain):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        res = ""
        try:
            s.connect((whois_server, 43))
            s.settimeout(5.0)
            msg = domain + "\r\n"
            s.sendall(msg.encode("utf-8"))
            r = ""
            while True:
                buffer = s.recv(512)
                if not buffer:
                    break
                r += buffer.decode("utf-8")

            res = r.replace("\r\n", "\n")
        except Exception:
            logging.exception("exc")
        finally:
            s.close()
        return res

    @staticmethod
    def _org_request(domain):
        res = Whois._whois_request("whois.pir.org", domain)

        try:
            name, registrar, create_date, update_date, exp_date = "", "", None, None, None

            for line in list(filter(lambda x: "%" not in x, res.split("\n"))):
                try:
                    data = [item.strip() for item in line.split(":", maxsplit=1)]
                    data[0] = data[0].lower()
                    if data[0] == "domain name":
                        name = data[1]
                    elif data[0] == "registrar":
                        registrar = data[1]
                    elif data[0] == "creation date" and not create_date:
                        create_date = datetime.datetime.strptime(data[1], "%Y-%m-%dT%H:%M:%SZ")
                    elif data[0] == "updated date" and not update_date:
                        update_date = datetime.datetime.strptime(data[1], "%Y-%m-%dT%H:%M:%SZ")
                    elif data[0] == "registry expiry date" and not exp_date:
                        exp_date = datetime.datetime.strptime(data[1], "%Y-%m-%dT%H:%M:%SZ")
                except Exception:
                    logging.exception("whois com parse")

            return Whois.Response(name, registrar, create_date, update_date, exp_date)
        except:
            pass
        return Whois.Response()

    @staticmethod
    def _com_request(domain):
        res = Whois._whois_request("whois.verisign-grs.com", domain)

        try:
            name, registrar, create_date, update_date, exp_date = "", "", None, None, None

            for line in list(filter(lambda x: "%" not in x, res.split("\n"))):
                try:
                    data = [item.strip() for item in line.split(":", maxsplit=1)]
                    data[0] = data[0].lower()
                    if data[0] =="domain name":
                        name = data[1]
                    elif data[0] == "registrar":
                        registrar = data[1]
                    elif data[0] == "creation date" and not create_date:
                        create_date = datetime.datetime.strptime(data[1], "%Y-%m-%dT%H:%M:%SZ")
                    elif data[0] == "updated date" and not update_date:
                        update_date = datetime.datetime.strptime(data[1], "%Y-%m-%dT%H:%M:%SZ")
                    elif data[0] == "registry expiry date" and not exp_date:
                        exp_date = datetime.datetime.strptime(data[1], "%Y-%m-%dT%H:%M:%SZ")
                except Exception:
                    logging.exception("whois com parse")

            return Whois.Response(name, registrar, create_date, update_date, exp_date)
        except:
            pass
        return Whois.Response()


    @staticmethod
    def _ua_request(domain):
        res = Whois._whois_request("whois.ua", domain)

        try:
            name, registrar, create_date, update_date, exp_date = "", "", None, None, None

            for line in list(filter(lambda x: "%" not in x, res.split("\n"))):
                try:
                    data = [item.strip() for item in line.split(":", maxsplit=1)]
                    data[0] = data[0].lower()
                    if data[0] =="domain":
                        name = data[1]
                    elif data[0] == "registrant":
                        registrar = data[1]
                    elif data[0] == "created" and not create_date:
                        create_date = datetime.datetime.strptime(data[1]+"00", "%Y-%m-%d %H:%M:%S%z")
                    elif data[0] == "modified" and not update_date:
                        update_date = datetime.datetime.strptime(data[1]+"00", "%Y-%m-%d %H:%M:%S%z")
                    elif data[0] == "expires" and not exp_date:
                        exp_date = datetime.datetime.strptime(data[1]+"00", "%Y-%m-%d %H:%M:%S%z")
                except Exception:
                    logging.exception("whois ua parse")

            return Whois.Response(name, registrar, create_date, update_date, exp_date)
        except:
            pass
        return Whois.Response()

    @staticmethod
    def _ru_request(domain):
        res = Whois._whois_request("whois.tcinet.ru", domain)

        try:
            name, registrar, create_date, update_date, exp_date = "", "", None, None, None

            for line in list(filter(lambda x: "%" not in x, res.split("\n"))):
                try:
                    data = [item.strip() for item in line.split(":", maxsplit=1)]
                    data[0] = data[0].lower()
                    if data[0] == "domain":
                        name = data[1]
                    elif data[0] == "registrar":
                        registrar = data[1]
                    elif data[0] == "created" and not create_date:
                        create_date = datetime.datetime.strptime(data[1], "%Y-%m-%dT%H:%M:%SZ")
                    elif data[0] == "paid-till" and not exp_date:
                        exp_date = datetime.datetime.strptime(data[1], "%Y-%m-%dT%H:%M:%SZ")
                except Exception:
                    logging.exception("whois ua parse")

            return Whois.Response(name, registrar, create_date, update_date, exp_date)
        except:
            pass
        return Whois.Response()
