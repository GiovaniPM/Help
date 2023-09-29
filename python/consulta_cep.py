from pycep_correios import get_address_from_cep, WebService, exceptions

try:

    address = get_address_from_cep('37503-130', webservice=WebService.APICEP)

except exceptions.InvalidCEP as eic:
    print(eic)

except exceptions.CEPNotFound as ecnf:
    print(ecnf)

except exceptions.ConnectionError as errc:
    print(errc)

except exceptions.Timeout as errt:
    print(errt)

except exceptions.HTTPError as errh:
    print(errh)

except exceptions.BaseException as e:
    print(e)