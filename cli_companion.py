from plac import call
from os import environ
from InquirerPy.inquirer import text
import openai

def main():
    if 'CHATKEY' not in environ: raise Exception('Set CHARKEY')
    openai.api_key = environ['CHATKEY']

    prompt = text('What do you want to ask?').execute()
    print(prompt)
    completions = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )

    generated_text = completions.choices[0].text
    print(generated_text)
    
    
if __name__ == '__main__':
    call(main)    