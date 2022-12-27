from typing import Dict
from plac import Interpreter
from pathlib import Path
from os import environ
from InquirerPy.inquirer import text, fuzzy, select
from toolbox.companion_logger import logger
import openai
import shelve


cwd = Path(__file__).parent

cwd = cwd if cwd.name == 'chat_cli' else cwd.parent.parent

class Companion(object):
    
    commands = [
                'generate_response',
                'talk', 
                'summarize', 
                'review',
                'make_history',
                'resummarize'
                ]
    
    
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
         
    def generate_response(self,
            prompt: ('Your propmt','positional'),
            engine: ('The engine you use davinci|curie|ada','option','e',)='davinci',
            max_tokens:('max tokens used in response','option','max')=1024,
            n: ('The number of generated','option')=1,
            temperature: ('1 for more random','option','t') = 0.5,
            filename:('The file name to output review for example scrach.py','option','f')='',
            )->str:
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
        response = select('Choose Response',
                          choices={c.text for c in completions.choices} 
                            ).execute() if n > 1 else completions.choices[0].text
        
        if filename:
            (Path()/filename).write_text(response)
        
        return response
        
    def talk(self,
            prompt: ('Your propmt','positional')='',
            engine: ('The engine you use davinci|curie|ada','option','e',)='davinci',
            max_tokens:('max tokens used in response','option','max')=1024,
            n: ('The number of generated','option')=1,
            temperature: ('1 for more random','option','t') = 0.5,
            filename:('The file name to output review for example scrach.py','option','f')='',
            profile:('The profile to load in from contexts','option','p')='default',
            )->str:
        '''
        This allows you save your companion's responses, they are stored in context.db.
        '''
        
        logger.prompt((prompt:=prompt or text('What do you want to ask?').execute()))
        logger.response((response:=self.generate_response(
                              prompt=prompt,
                              engine=engine,
                              max_tokens=max_tokens,
                              n=n,
                              temperature=temperature,
        )))
        logger.summary((summary := self.summarize(
                                    prompt=f'I said "{prompt}". And you responded with "{response}"',
                                    t='conversations',
                                    engine=engine,
                                    n=n,
                                    temperature=temperature,
                        )))
       
        with shelve.open(str(cwd/'.contexts')) as hst:
            if profile not in hst: hst[profile] = {'history':{}}
            hst[profile]['history'][prompt] = {'response':response,'summary':summary}
        
        if filename:(Path()/filename).write_text(response)
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
        with shelve.open(str(cwd/'.contexts')) as hst:
            prompt = fuzzy('What prompt do you want to review', 
                            choices=list(hst['history'].keys()),
                            vi_mode=True,
                            ).execute()
        response = hst[profile]['history'][prompt]['summary' if summary else 'response']
        if filename:(Path()/filename).write_text(response)
        return response
         
    def make_history(self,
                     profile:('The profile to load in from contexts','option','p')='default',
                     )->Dict[str,Dict[str,str]]:

        '''
        rebuilds history from log
        '''

        txt = [[l for l in t.split('\n') if l.strip() and l!='?'] 
        for t in (cwd / 'log/companion_0.log').read_text().split('##########\n')]
        txt = [t for t in txt if t]
        response = [t[-1] for t in txt if 'RESPONSE' in t[0]]
        prompts = [t[-1] for t in txt if 'PROMPT' in t[0]]
        summary = [t[-1] for t in txt if 'SUMMARY' in t[0]]
        conversations = {p:{'response':r, 'summary':s} for p,r,s in zip(prompts,response,summary)}
        with shelve.open(str(cwd/'.contexts')) as hst:
            hst[profile]['history'] = conversations
        return conversations

    def resummarize(self,
                     profile:('The profile to load in from contexts','option','p')='default',
                     )->Dict[str,Dict[str,str]]:

        '''
        creates an updated summaries for questions.
        '''
        with shelve.open(str(cwd/'.contexts')) as hst:
                hst[profile]['history'] |= {k:{j: (r:=u) if j == 'response' 
                                                         else self.summarize(f'I said this {k}, and you responded with {r}') 
                                            for j,u in v.items()} 
                                            for k,v in hst[profile]['history'].items()}
                conversations = hst[profile]['history']
        return conversations
       
if __name__ == '__main__':
    Interpreter.call(Companion)   