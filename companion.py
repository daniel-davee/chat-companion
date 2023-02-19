from typing import Dict, List
from plac import Interpreter
from pathlib import Path
from os import environ
from InquirerPy.inquirer import text, fuzzy, select
from toolbox.companion_logger import logger
from toolbox.prompt_tools import clean_f_str
import openai
import shelve


cwd = Path(__file__).parent

cwd = cwd if cwd.name == 'chat_cli' else cwd.parent.parent

contexts = cwd / ".contexts/contexts.dat"
contexts.parent.mkdir(exist_ok=True)
contexts = '.'.join(contexts.as_posix().split('.')[:-1])
logs = cwd / "log"
logs.mkdir(exist_ok=True)
class Companion(object):
    
    commands = [
                'generate_response',
                'talk', 
                'summarize', 
                'review',
                'resummarize',
                'translate',
                'proof_read',
                ]
    
    def proof_read(self,
                   prompt:('The prompt you want to proof read','positional'),
                   temperature: ('1 for more random','option','t') = 0.5,
                   ):
        prompt = clean_f_str(f'''
                             Proof read this '{prompt or 
                             text('What do you want to proof read?')
                             .execute()}',
                             and correct any spelling or grammar mistakes.
                            ''')
        return self.generate_response(prompt,temperature) 
    
    def translate(self,
                  prompt:('The prompt you want translated','positional'),
                  language:(f'The language you want to translate to','option','l')='english',
                  temperature: ('1 for more random','option','t') = 0.5,
                  ):
        prompt = clean_f_str(f'''Translate this '{prompt or 
                                 text('What do you want to translate?')
                                 .execute()}' into {language}''')
        return self.generate_response(prompt,temperature) 
    
    def generate_response(self,
            prompt: ('Your propmt','positional'),
            temperature: ('1 for more random','option','t') = 0.5,
            engine: ('The engine you use davinci|curie|ada','option','e',)='davinci',
            max_tokens:('max tokens used in response','option','max')=1024,
            n: ('The number of generated','option')=1,
            filename:('The file name to output review for example scrach.py','option','f')='',
            bulk:('If set will return all responses as a list','flag','b')=False,
            )->str or List[str]:
        '''
        This Generates a response, it doesn't store it context.db.
        '''
        if 'CHATKEY' not in environ: raise Exception('Set CHATKEY')
        openai.api_key = environ['CHATKEY']
        completions = openai.Completion.create(
                                        engine=f"text-{engine}-{'002' if engine == 'davinci' else '001'}",
                                        prompt=prompt,
                                        max_tokens=max_tokens,
                                        n=n,
                                        stop=None,
                                        temperature=temperature,
                                        )
        choices = [c.text for c in completions.choices]
        response = choices if bulk else \
                   select('Choose Response',choices=choices ).execute() if n > 1 \
                   else completions.choices[0].text
        
        if filename:
            (Path()/filename).write_text(response)
        
        return response
    
    def summarize(self, 
                    prompt: ('Your propmt','positional')='',
                    engine: ('The engine you use davinci|curie|ada','option','e',)='davinci',
                    n: ('The number of generated','option')=1,
                    temperature: ('1 for more random','option','t') = 0.5,
                    t: ('1 for more random','option','type') = '',
                  ) -> str:
        '''
        Summarizes input
        '''
        return self.generate_response(
                              prompt=f'Summarize this {t} {prompt} concisely',
                              engine=engine,
                              max_tokens=3000,
                              n=n,
                              temperature=temperature,
                          )
        
        
    def talk(self,
            prompt: ('Your propmt','positional')='',
            engine: ('The engine you use davinci|curie|ada','option','e',)='davinci',
            max_tokens:('max tokens used in response','option','max')=1024,
            n: ('The number of generated','option')=1,
            temperature: ('1 for more random','option','t') = 0.5,
            filename:('The file name to output review for example scrach.py','option','f')='',
            profile:('The profile to load in from contexts','option','p')='default',
            in_file:('File that is input to the prompt use {in_file} to reference it','option','In')='',
            **kwargs,
            )->str:
        '''
        This allows you save your companion's responses, they are stored in context.db.
        ''' 
        prompt = prompt or text('What do you want to ask?').execute()
        if in_file or kwargs:
            if in_file: kwargs['in_file'] = Path(in_file).read_text()
            prompt = [s.split('{') for s in prompt.split('}') if s]
            end =prompt[-1][0] if len(prompt[-1]) < 2 else ''
            prompt = [s for s in prompt if len(s) ==2]
            prompt = ''.join([f'{k}{kwargs[v]}' for k,v in prompt])+end
        
        logger.prompt(prompt)
        logger.response((response:=self.generate_response(
                              prompt=prompt,
                              engine=engine,
                              max_tokens=max_tokens,
                              n=n,
                              temperature=temperature,
                              filename=filename
        )))
        
        logger.summary((summary := self.summarize(
                                    prompt=f'you said to me "{prompt}". and I responded back to you with "{response}"',
                                    t='conversations between you and me',
                                    engine=engine,
                                    n=n,
                                    temperature=temperature,
                        )))
       
        with shelve.open(contexts, writeback=True) as hst:
            if profile not in hst: hst[profile] = {'history':{}}
            hst[profile]['history'] |= {prompt:{'response':response,'summary':summary}}
        
        return response
   
    def review(self,
               filename:('The file name to output review for example scrach.py','option','f')='',
               profile:('The profile to load in from contexts','option','p')='default',
               summary:('show summary','flag','s')=False,
               )->str:
        '''
        To review previous questions and responses,
        use the `review` subcommand. This will bring up a list of previous questions.
        You can then select a question to view the response.
        '''
        with shelve.open(contexts, writeback=True) as hst:
            if profile not in hst: 
                hst[profile] = {'history':{}}
                return 'No history yet'
            prompt = fuzzy('What prompt do you want to review', 
                            choices=list(hst[profile]['history'].keys()),
                            vi_mode=True,
                            ).execute()
            response = hst[profile]['history'][prompt]['summary' if summary else 'response']
        if filename:(Path()/filename).write_text(response)
        return response

    def resummarize(self,
                     profile:('The profile to load in from contexts','option','p')='default',
                     n: ('The number of generated','option')=1,
                     temperature: ('1 for more random','option','t') = 0.75,
                     )->Dict[str,Dict[str,str]]:

        '''
        creates an updated summary for question.
        '''
        with shelve.open(contexts, writeback=True) as hst:
            if profile not in hst: 
                hst[profile] = {'history':{}}
                return 'No history yet'
            logger.prompt((prompt:=fuzzy('What prompt do you want to review', 
                            choices=list(hst[profile]['history'].keys()),
                            vi_mode=True,
                            ).execute()))
            logger.response((response:=hst[profile]['history'][prompt]['response']))
            logger.summary((summary := self.summarize(
                                        prompt=f'you said to me "{prompt}". and I responded back to you with "{response}"',
                                        t='conversations between you and me',
                                        n=n,
                                        temperature=temperature,
                            )))
            hst[profile]['history'][prompt]= {'response':response, 'summary':summary}
            return summary
            
       
if __name__ == '__main__':
    Interpreter.call(Companion)   