from plac import call
from os import environ
from InquirerPy.inquirer import text
import openai
from toolbox.companion_logger import logger

def main(
        prompt: ('Your propmt','positional')='',
        engine: (
                    'The engine you use davinci|curie|ada',
                    'option','e',
                 )='davinci',
        max_tokens:('max tokens used in response','option','max')=1024,
        n: ('The number of generated','option')=1,
        temperature: ('1 for more random','option','t') = 0.5,
                                    ):
    if 'CHATKEY' not in environ: raise Exception('Set CHARKEY')
    openai.api_key = environ['CHATKEY']

    logger.prompt((prompt:=prompt 
                        or text('What do you want to ask?').execute()))
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
    
    
if __name__ == '__main__':
    call(main)    