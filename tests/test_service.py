from hrc.core import Core

core = Core(config_dict={'core':{'services':['hrc.service.console', 'hrc.service.http']}})

core.run()