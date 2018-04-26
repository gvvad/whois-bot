import socket
import logging
import datetime


class Whois(object):

    class Response(object):
        def __init__(self,
                     name=None,
                     registrar=None,
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
        zone = domain.split(".")[-1]
        try:
            if zone == "ua":
                return Whois._ua_request(domain)
            else:
                return Whois.Response()
        except Exception:
            return Whois.Response()

    @staticmethod
    def _ua_request(domain):
        whois_server = "whois.ua"
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        res = ""
        try:
            s.connect((whois_server, 43))
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

        try:
            name = None
            registrar = None
            create_date = None
            update_date = None
            exp_date = None

            for line in list(filter(lambda x: "%" not in x, res.split("\n"))):
                try:
                    data = [item.strip() for item in line.split(":", maxsplit=1)]
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
                    logging.exception("whois parse")
                    pass

            return Whois.Response(name, registrar, create_date, update_date, exp_date)
        except:
            pass
        return Whois.Response()
