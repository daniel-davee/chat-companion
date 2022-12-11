from pysimplelog import Logger

logger = Logger('cli_companion')
logger.set_log_file_basename('log/companion')
logger.set_minimum_level(logger.logLevels['info'])
logger.set_maximum_level(100,fileFlag=False)

logger.add_log_type("prompt", name="PROMPT", 
                    level=200, color='blue', )
logger.add_log_type("response", name="RESPONSE", 
                    level=200, color='blue', )

def response(msg:str,*args,**kwargs):
    logger.log('response', 
             f'''
{msg}
{'#'*10}
             ''', 
             *args, **kwargs)

def prompt(msg:str,*args,**kwargs):
    logger.log('prompt', 
             f'''
{msg}
{'#'*10}
             ''', 
             *args, **kwargs)
    
logger.response = response
logger.prompt =prompt 