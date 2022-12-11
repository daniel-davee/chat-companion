from plac import Interpreter
from pathlib import Path
from os import environ
from InquirerPy.inquirer import text, fuzzy
from toolbox.companion_logger import logger
import openai
import shelve

class Companion(object):
    commands = 'talk', 'review'
    
    def talk(self,
            prompt: ('Your propmt','positional')='',
            engine: (
                        'The engine you use davinci|curie|ada',
                        'option','e',
                    )='davinci',
            max_tokens:('max tokens used in response','option','max')=1024,
            n: ('The number of generated','option')=1,
            temperature: ('1 for more random','option','t') = 0.5,
                filename:('''The file name to output review
                            for example scrach.py
                        ''','option','f')='',
                                        ):
        '''
        Allows you to talk chat gpt
        '''
        if 'CHATKEY' not in environ: raise Exception('Set CHARKEY')
        openai.api_key = environ['CHATKEY']

        logger.prompt((prompt:=prompt 
                            or text('What do you want to ask?').execute()),
                      )
        completions = openai.Completion.create(
            engine=f"text-{engine}-{'002' if engine == 'davinci' else '001'}",
            prompt=prompt,
            max_tokens=max_tokens,
            n=n,
            stop=None,
            temperature=temperature,
        )
        print((generated_text:=completions.choices[0].text))
        logger.response(generated_text)
        with shelve.open('.history') as hst:
            hst['history'] |= {prompt:generated_text}
        
        if filename:(Path()/filename).write_text(generated_text)
   
    def review(self,
               filename:('''The file name to output review
                            for example scrach.py
                         ''','option','f')='',
               ):
        '''
        To review previous questions and responses,
        use the `review` subcommand. This will bring up a list of previous questions.
        You can then select a question to view the response.
        '''
        with shelve.open('.history') as hst:
            prompt = fuzzy('What prompt do you want to review', 
                            choices=list(hst['history'].keys()),
                            vi_mode=True,
                            ).execute()
            print((response:=hst['history'][prompt]))
        if filename:(Path()/filename).write_text(response)
       
if __name__ == '__main__':
    Interpreter.call(Companion)   